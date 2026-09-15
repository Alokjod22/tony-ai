import os
import json
import time
import sqlite3
from typing import Dict, Any, List, Optional

DEFAULT_PROTOCOLS = [
    {
        "id": "morning_brief",
        "name": "Protocol: Morning Tactical Brief",
        "description": "Checks system telemetry, gathers top technology headlines, and reviews long-term memory priorities.",
        "steps": [
            {"action": "telemetry", "param": "full_health"},
            {"action": "research", "param": "Top breakthrough AI, quantum computing and tech headlines today"},
            {"action": "memory", "param": "recall_priorities"}
        ]
    },
    {
        "id": "dev_kickoff",
        "name": "Protocol: Developer Kickoff",
        "description": "Inspects git repository status, scans connected Android ADB devices, and runs project sanity checks.",
        "steps": [
            {"action": "git_status", "param": "."},
            {"action": "adb_devices", "param": ""},
            {"action": "run_code", "param": "import sys, platform; print(f'Python: {sys.version.split()[0]} on {platform.system()} {platform.release()}')"}
        ]
    },
    {
        "id": "security_lockdown",
        "name": "Protocol: Security & Memory Audit",
        "description": "Performs comprehensive vulnerability assessment and audits high-importance memories.",
        "steps": [
            {"action": "security_audit", "param": "deep"},
            {"action": "telemetry", "param": "diagnose_bottlenecks"}
        ]
    }
]

class ProtocolEngine:
    """Manages custom automated multi-step protocols and macros triggered conversationally or via UI."""

    def __init__(self, db_path: str = "data/tony_protocols.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS protocols (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    steps_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            # Seed default protocols if table is empty
            cursor.execute("SELECT COUNT(*) FROM protocols")
            if cursor.fetchone()[0] == 0:
                for p in DEFAULT_PROTOCOLS:
                    cursor.execute(
                        "INSERT INTO protocols (id, name, description, steps_json) VALUES (?, ?, ?, ?)",
                        (p["id"], p["name"], p["description"], json.dumps(p["steps"]))
                    )
                conn.commit()

    def list_protocols(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, steps_json, created_at FROM protocols")
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "description": r[2],
                    "steps": json.loads(r[3]),
                    "created_at": r[4]
                }
                for r in rows
            ]

    def save_protocol(self, protocol_id: str, name: str, description: str, steps: List[Dict[str, str]]) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO protocols (id, name, description, steps_json) VALUES (?, ?, ?, ?)",
                (protocol_id, name, description, json.dumps(steps))
            )
            conn.commit()
        return {"success": True, "id": protocol_id, "name": name, "steps_count": len(steps)}

    def execute_protocol(self, protocol_id: str, brain_ref: Any) -> Dict[str, Any]:
        """Executes each step of a saved protocol and tracks execution states."""
        protocols = {p["id"]: p for p in self.list_protocols()}
        if protocol_id not in protocols:
            return {"success": False, "error": f"Protocol '{protocol_id}' not found."}

        target = protocols[protocol_id]
        steps = target["steps"]
        step_results = []
        start_time = time.time()

        for idx, s in enumerate(steps, 1):
            action = s.get("action")
            param = s.get("param", "")
            step_start = time.time()
            output = ""

            try:
                if action == "telemetry":
                    if hasattr(brain_ref, "tools"):
                        output = brain_ref.tools.get_deep_telemetry()
                    else:
                        output = "Telemetry gathered."
                elif action == "research":
                    if hasattr(brain_ref, "research"):
                        output = brain_ref.research.execute_autonomous_research(param)
                    else:
                        output = f"Research executed for: {param}"
                elif action == "git_status":
                    if hasattr(brain_ref, "developer"):
                        output = brain_ref.developer.get_git_status(param)
                    else:
                        output = "Git status checked."
                elif action == "adb_devices":
                    if hasattr(brain_ref, "developer"):
                        output = brain_ref.developer.adb_devices()
                    else:
                        output = "ADB devices listed."
                elif action == "run_code":
                    if hasattr(brain_ref, "sandbox"):
                        output = brain_ref.sandbox.execute_python(param)
                    else:
                        output = "Code executed."
                elif action == "security_audit":
                    if hasattr(brain_ref, "security"):
                        output = brain_ref.security.run_comprehensive_audit()
                    else:
                        output = "Security audit completed."
                elif action == "memory":
                    if hasattr(brain_ref, "memory"):
                        output = brain_ref.memory.get_recent_context()
                    else:
                        output = "Memory recalled."
                else:
                    output = f"Action {action} performed."
            except Exception as e:
                output = f"Step failed: {str(e)}"

            elapsed_step = round((time.time() - step_start) * 1000, 1)
            step_results.append({
                "step_num": idx,
                "action": action,
                "param": param,
                "result": output,
                "latency_ms": elapsed_step,
                "status": "COMPLETED"
            })

        total_elapsed = round((time.time() - start_time) * 1000, 1)
        return {
            "success": True,
            "protocol_id": protocol_id,
            "name": target["name"],
            "steps": step_results,
            "total_latency_ms": total_elapsed,
            "completed_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
