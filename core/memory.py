import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from config import DB_PATH

class MemoryEngine:
    """Persistent SQLite-backed cognitive memory and knowledge core for Tony AI."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

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
            # Structured Long-Term Memory (facts, preferences, projects, habits)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT DEFAULT 'fact',
                    content TEXT NOT NULL,
                    importance INTEGER DEFAULT 3,
                    tags TEXT DEFAULT '[]',
                    created_at REAL,
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
                    persona TEXT DEFAULT 'tony',
                    created_at REAL
                )
            """)
            # Security & Action Audit Logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    target TEXT,
                    status TEXT,
                    security_level TEXT,
                    details TEXT,
                    timestamp REAL
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

    # --- Structured Long-Term Memory Core ---
    def add_memory(self, content: str, category: str = "fact", importance: int = 3, tags: Optional[List[str]] = None) -> int:
        tags_json = json.dumps(tags or [])
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (category, content, importance, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (category, content.strip(), int(importance), tags_json, now, now)
            )
            conn.commit()
            return cursor.lastrowid

    def get_memories(self, category: Optional[str] = None, min_importance: int = 1, limit: int = 100) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    "SELECT id, category, content, importance, tags, created_at, updated_at FROM memories WHERE category = ? AND importance >= ? ORDER BY importance DESC, updated_at DESC LIMIT ?",
                    (category, min_importance, limit)
                )
            else:
                cursor.execute(
                    "SELECT id, category, content, importance, tags, created_at, updated_at FROM memories WHERE importance >= ? ORDER BY importance DESC, updated_at DESC LIMIT ?",
                    (min_importance, limit)
                )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                try:
                    t_list = json.loads(r[4])
                except Exception:
                    t_list = []
                results.append({
                    "id": r[0],
                    "category": r[1],
                    "content": r[2],
                    "importance": r[3],
                    "tags": t_list,
                    "created_at": r[5],
                    "updated_at": r[6]
                })
            return results

    def search_memories(self, query: str) -> List[Dict[str, Any]]:
        query_pattern = f"%{query.lower()}%"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, category, content, importance, tags, created_at FROM memories WHERE LOWER(content) LIKE ? OR LOWER(category) LIKE ? OR LOWER(tags) LIKE ? ORDER BY importance DESC",
                (query_pattern, query_pattern, query_pattern)
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                try:
                    t_list = json.loads(r[4])
                except Exception:
                    t_list = []
                results.append({
                    "id": r[0],
                    "category": r[1],
                    "content": r[2],
                    "importance": r[3],
                    "tags": t_list,
                    "created_at": r[5]
                })
            return results

    def delete_memory(self, memory_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0

    def summarize_what_i_remember(self) -> Dict[str, Any]:
        """Generates a structured overview of all user memory and knowledge."""
        all_mem = self.get_memories(limit=200)
        kv = self.get_all_kv()

        facts = [m["content"] for m in all_mem if m["category"] in ("fact", "general")]
        prefs = [m["content"] for m in all_mem if m["category"] in ("preference", "pref")]
        projects = [m["content"] for m in all_mem if m["category"] in ("project", "work")]
        habits = [m["content"] for m in all_mem if m["category"] in ("habit", "workflow")]

        return {
            "total_memories": len(all_mem),
            "user_preferences": prefs,
            "facts_about_user": facts,
            "active_projects": projects,
            "custom_configurations": kv,
            "all_entries": all_mem
        }

    def export_memory_data(self) -> str:
        data = {
            "version": "3.0",
            "exported_at": time.time(),
            "kv_store": self.get_all_kv(),
            "memories": self.get_memories(limit=1000),
            "recent_tasks": self.get_tasks()
        }
        return json.dumps(data, indent=2)

    def import_memory_data(self, json_str: str) -> Dict[str, Any]:
        try:
            data = json.loads(json_str)
            imported_count = 0
            if "memories" in data and isinstance(data["memories"], list):
                for m in data["memories"]:
                    self.add_memory(
                        content=m.get("content", ""),
                        category=m.get("category", "fact"),
                        importance=m.get("importance", 3),
                        tags=m.get("tags", [])
                    )
                    imported_count += 1
            if "kv_store" in data and isinstance(data["kv_store"], dict):
                for k, v in data["kv_store"].items():
                    self.set(k, v)
            return {"status": "success", "imported_count": imported_count}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # --- Key-Value Engine ---
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

    # --- Conversation Logs ---
    def add_message(self, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None, persona: str = "tony"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation_history (role, content, tool_calls, persona, created_at) VALUES (?, ?, ?, ?, ?)",
                (role, content, json.dumps(tool_calls) if tool_calls else None, persona, time.time())
            )
            conn.commit()

    def get_recent_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, tool_calls, persona, created_at FROM conversation_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            history = []
            for r in reversed(rows):
                history.append({
                    "role": r[0],
                    "content": r[1],
                    "tool_calls": json.loads(r[2]) if r[2] else None,
                    "persona": r[3] if len(r) > 3 else "tony",
                    "created_at": r[4] if len(r) > 4 else None
                })
            return history

    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversation_history")
            conn.commit()

    # --- Audit Logging ---
    def log_audit(self, action: str, target: str, status: str, security_level: str = "ASSIST", details: str = ""):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_log (action, target, status, security_level, details, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (action, target, status, security_level, details, time.time())
            )
            conn.commit()

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, action, target, status, security_level, details, timestamp FROM audit_log ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            logs = []
            for r in rows:
                logs.append({
                    "id": r[0],
                    "action": r[1],
                    "target": r[2],
                    "status": r[3],
                    "security_level": r[4],
                    "details": r[5],
                    "timestamp": r[6]
                })
            return logs

    # --- Tasks & Reminders ---
    def add_task(self, task_text: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (task_text, created_at) VALUES (?, ?)",
                (task_text, time.time())
            )
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT id, task_text, status, created_at FROM tasks WHERE status = ? ORDER BY id DESC", (status,))
            else:
                cursor.execute("SELECT id, task_text, status, created_at FROM tasks ORDER BY id DESC")
            return [{"id": r[0], "text": r[1], "status": r[2], "created_at": r[3]} for r in cursor.fetchall()]

    def complete_task(self, task_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ?", (time.time(), task_id))
            conn.commit()
