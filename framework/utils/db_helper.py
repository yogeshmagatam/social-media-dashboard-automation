"""
Database Verification Utility for Pytest.
Directly executes SQL queries against SQLite to assert backend data persistence
and transaction integrity during UI test executions.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from framework.config.config import DB_PATH
from framework.utils.logger import get_logger
from app.database import init_db

logger = get_logger("DBHelper")


class DatabaseHelper:
    def __init__(self, db_file=DB_PATH):
        self.db_file = str(db_file)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def reset_database(self):
        """Resets the database to clean seed state before/after test suites."""
        logger.info(f"Resetting database at {self.db_file}")
        init_db(seed=True)

    def query_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns all rows as list of dicts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def query_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Executes a SELECT query and returns the first row or None."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # ================= Specialized Verification Queries =================

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Verifies user existence and details via SQL."""
        sql = "SELECT id, username, full_name, email, role, created_at FROM users WHERE username = ?"
        return self.query_one(sql, (username,))

    def get_post_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Fetches post by ID to assert UI deletion or creation."""
        sql = "SELECT * FROM posts WHERE id = ?"
        return self.query_one(sql, (post_id,))

    def get_latest_post_by_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetches the latest post created by a specific user."""
        sql = """
            SELECT p.*, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE u.username = ?
            ORDER BY p.id DESC
            LIMIT 1
        """
        return self.query_one(sql, (username,))

    def get_post_count(self, username: Optional[str] = None, platform: Optional[str] = None) -> int:
        """Counts total posts in the database, optionally filtered by user and platform."""
        sql = "SELECT COUNT(*) as count FROM posts p JOIN users u ON p.user_id = u.id WHERE 1=1"
        params = []
        if username:
            sql += " AND u.username = ?"
            params.append(username)
        if platform and platform != "All":
            sql += " AND p.platform = ?"
            params.append(platform)

        res = self.query_one(sql, tuple(params))
        return res["count"] if res else 0

    def get_user_metrics(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetches metrics record for a user via SQL."""
        sql = """
            SELECT m.*, u.username
            FROM metrics m
            JOIN users u ON m.user_id = u.id
            WHERE u.username = ?
        """
        return self.query_one(sql, (username,))

    def get_latest_audit_log(self, action: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetches latest audit log entry to verify event tracking."""
        sql = "SELECT * FROM audit_logs"
        params = []
        if action:
            sql += " WHERE action = ?"
            params.append(action)
        sql += " ORDER BY id DESC LIMIT 1"
        return self.query_one(sql, tuple(params))

    def count_audit_logs(self, action: str) -> int:
        """Counts occurrences of an action in audit_logs."""
        sql = "SELECT COUNT(*) as count FROM audit_logs WHERE action = ?"
        res = self.query_one(sql, (action,))
        return res["count"] if res else 0
