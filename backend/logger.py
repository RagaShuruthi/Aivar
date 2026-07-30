import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List

LOG_DB_PATH = os.path.join(os.path.dirname(__file__), "audit.db")

class AuditLogger:
    """Immutable Audit Logging Service for governance and observability."""

    def __init__(self, db_path: str = LOG_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    customer_id INTEGER,
                    allowed BOOLEAN NOT NULL,
                    reason TEXT NOT NULL
                )
            """)
            conn.commit()

    def log(
        self,
        user: str,
        agent: str,
        operation: str,
        customer_id: int,
        allowed: bool,
        reason: str
    ) -> int:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_logs (timestamp, user, agent, operation, customer_id, allowed, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (timestamp, user, agent, operation, customer_id, allowed, reason)
            )
            conn.commit()
            return cursor.lastrowid

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

# Instantiated Singleton AuditLogger
audit_logger = AuditLogger()
