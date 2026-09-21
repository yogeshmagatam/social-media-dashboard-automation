"""
Database initialization, schema management, and seeding for the Social Media Dashboard.
Uses SQLite for self-contained, zero-setup testing and SQL validation.
"""

import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "database" / "social_dashboard.db"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_db_connection(db_path: Path = DB_FILE) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_FILE, seed: bool = True):
    """Creates database tables and optionally seeds default test data."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        DROP TABLE IF EXISTS audit_logs;
        DROP TABLE IF EXISTS metrics;
        DROP TABLE IF EXISTS posts;
        DROP TABLE IF EXISTS users;

        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'creator',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            media_url TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            total_followers INTEGER DEFAULT 0,
            total_impressions INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()

    if seed:
        seed_data(conn)

    conn.close()


def seed_data(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Seed demo users
    users = [
        ("admin", hash_password("Admin@123"), "Alex Rivera", "alex@socialpulse.io", "admin"),
        ("testuser", hash_password("Password@123"), "Sarah Connor", "sarah@socialpulse.io", "creator"),
        ("qa_tester", hash_password("QASecret#2026"), "David Miller", "david@socialpulse.io", "tester")
    ]

    cursor.executemany(
        "INSERT INTO users (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
        users
    )

    # Fetch user IDs
    cursor.execute("SELECT id, username FROM users")
    user_map = {row["username"]: row["id"] for row in cursor.fetchall()}

    # Seed metrics
    cursor.execute(
        """INSERT INTO metrics (user_id, total_followers, total_impressions, engagement_rate)
           VALUES (?, ?, ?, ?)""",
        (user_map["admin"], 124500, 985200, 5.8)
    )
    cursor.execute(
        """INSERT INTO metrics (user_id, total_followers, total_impressions, engagement_rate)
           VALUES (?, ?, ?, ?)""",
        (user_map["testuser"], 45200, 312000, 4.2)
    )

    # Seed sample posts
    posts = [
        (user_map["testuser"], "Twitter/X", "Excited to launch our automated QA testing pipeline with Playwright & Pytest! 🚀 #Automation #QA", None, 142, 18),
        (user_map["testuser"], "LinkedIn", "Why testing in production is a risk you can mitigate with full-stack automated regression suites.", None, 89, 24),
        (user_map["testuser"], "Instagram", "Workspace setup for today! Dual 4K monitors, ergonomic chair, and coffee running hot ☕✨", "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600", 312, 45),
        (user_map["testuser"], "YouTube", "Video Tutorial: End-to-end testing with Playwright, Pytest and SQL Database Validation.", None, 650, 110)
    ]

    cursor.executemany(
        "INSERT INTO posts (user_id, platform, content, media_url, likes_count, comments_count) VALUES (?, ?, ?, ?, ?, ?)",
        posts
    )

    # Initial audit log
    cursor.execute(
        "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
        (user_map["testuser"], "SYSTEM_SEED", "Initial database seed completed")
    )

    conn.commit()


if __name__ == "__main__":
    init_db()
    print(f"Database successfully initialized at: {DB_FILE}")
