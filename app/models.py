"""
Data Access Layer (Models) for Social Media Dashboard.
Provides clean query functions used by the web server and for verification.
"""

from typing import List, Optional, Dict, Any
from app.database import get_db_connection, hash_password


class UserModel:
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        pwd_hash = hash_password(password)
        cursor.execute(
            "SELECT id, username, full_name, email, role FROM users WHERE username = ? AND password_hash = ?",
            (username, pwd_hash)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_username(username: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, email, role, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None


class PostModel:
    @staticmethod
    def get_all(user_id: Optional[int] = None, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT p.id, p.user_id, u.username, u.full_name, p.platform, p.content,
                   p.media_url, p.likes_count, p.comments_count, p.status, p.created_at
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.status = 'published'
        """
        params = []

        if user_id:
            query += " AND p.user_id = ?"
            params.append(user_id)
        if platform and platform != "All":
            query += " AND p.platform = ?"
            params.append(platform)

        query += " ORDER BY p.created_at DESC, p.id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(user_id: int, platform: str, content: str, media_url: Optional[str] = None) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO posts (user_id, platform, content, media_url, likes_count, comments_count)
               VALUES (?, ?, ?, ?, 0, 0)""",
            (user_id, platform, content, media_url)
        )
        post_id = cursor.lastrowid

        # Record audit log
        cursor.execute(
            "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, "POST_CREATED", f"Post #{post_id} created for {platform}")
        )
        conn.commit()
        conn.close()
        return post_id

    @staticmethod
    def delete(post_id: int, user_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE id = ? AND user_id = ?", (post_id, user_id))
        affected = cursor.rowcount

        if affected > 0:
            cursor.execute(
                "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
                (user_id, "POST_DELETED", f"Post #{post_id} deleted")
            )
            conn.commit()

        conn.close()
        return affected > 0

    @staticmethod
    def like(post_id: int) -> Optional[int]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?", (post_id,))
        conn.commit()

        cursor.execute("SELECT likes_count FROM posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        conn.close()
        return row["likes_count"] if row else None


class MetricsModel:
    @staticmethod
    def get_by_user(user_id: int) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM metrics WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) as total_posts, SUM(likes_count) as total_likes FROM posts WHERE user_id = ?", (user_id,))
        post_stats = cursor.fetchone()

        conn.close()

        base_metrics = dict(row) if row else {
            "total_followers": 1250,
            "total_impressions": 8400,
            "engagement_rate": 3.2
        }

        base_metrics["total_posts"] = post_stats["total_posts"] if post_stats and post_stats["total_posts"] else 0
        base_metrics["total_likes"] = post_stats["total_likes"] if post_stats and post_stats["total_likes"] else 0
        return base_metrics


class AuditModel:
    @staticmethod
    def log(user_id: Optional[int], action: str, details: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, action, details)
        )
        conn.commit()
        conn.close()
