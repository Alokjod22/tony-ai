import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from config import DB_PATH

class MemoryEngine:
    """Persistent SQLite-backed memory store for Tony AI."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Key-value persistent knowledge & preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at REAL
                )
            """)
            # Conversation logs & interaction memory
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    tool_calls TEXT,
                    created_at REAL
                )
            """)
            # Reminders and tasks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_text TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at REAL,
                    completed_at REAL
                )
            """)
            conn.commit()

    def set(self, key: str, value: Any):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            val_str = json.dumps(value) if not isinstance(value, str) else value
            cursor.execute(
                "INSERT OR REPLACE INTO kv_store (key, value, updated_at) VALUES (?, ?, ?)",
                (key, val_str, time.time())
            )
            conn.commit()

    def get(self, key: str, default: Any = None) -> Any:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except Exception:
                    return row[0]
            return default

    def delete(self, key: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kv_store WHERE key = ?", (key,))
            conn.commit()

    def get_all_kv(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM kv_store")
            results = {}
            for k, v in cursor.fetchall():
                try:
                    results[k] = json.loads(v)
                except Exception:
                    results[k] = v
            return results

    def add_message(self, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation_history (role, content, tool_calls, created_at) VALUES (?, ?, ?, ?)",
                (role, content, json.dumps(tool_calls) if tool_calls else None, time.time())
            )
            conn.commit()

    def get_recent_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, tool_calls, created_at FROM conversation_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            history = []
            for r in reversed(rows):
                history.append({
                    "role": r[0],
                    "content": r[1],
                    "tool_calls": json.loads(r[2]) if r[2] else None,
                    "created_at": r[3]
                })
            return history

    def add_task(self, task_text: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (task_text, status, created_at) VALUES (?, 'pending', ?)",
                (task_text, time.time())
            )
            conn.commit()
            return cursor.lastrowid

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT id, task_text, status, created_at FROM tasks WHERE status = ? ORDER BY id DESC", (status,))
            else:
                cursor.execute("SELECT id, task_text, status, created_at FROM tasks ORDER BY id DESC")
            rows = cursor.fetchall()
            return [{"id": r[0], "task": r[1], "status": r[2], "created_at": r[3]} for r in rows]

    def complete_task(self, task_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ?",
                (time.time(), task_id)
            )
            conn.commit()

    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversation_history")
            conn.commit()
