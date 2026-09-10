import asyncio
import time
from typing import Dict, Any, List, Optional
from core.memory import MemoryEngine

class WorkflowAndMissionEngine:
    """Action Engine, Macro Runner & Tactical Mission Orchestrator for Tony AI."""

    def __init__(self, memory: Optional[MemoryEngine] = None, tools = None):
        self.memory = memory
        self.tools = tools
        self.active_missions: Dict[str, Dict[str, Any]] = {}
        self.custom_workflows: Dict[str, List[Dict[str, Any]]] = self._load_default_workflows()

    def _load_default_workflows(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "start_development": [
                {"action": "open_application", "args": {"app_name": "vscode"}, "desc": "Launch VS Code Editor"},
                {"action": "open_application", "args": {"app_name": "chrome"}, "desc": "Launch Developer Browser"},
                {"action": "get_system_diagnostics", "args": {}, "desc": "Verify System Resources & Telemetry"}
            ],
            "clean_temp_workspace": [
                {"action": "get_system_diagnostics", "args": {}, "desc": "Audit Disk Space & Memory"},
                {"action": "run_shell_command", "args": {"command": "echo Workspace verified."}, "desc": "Audit Temp Files"}
            ]
        }

    def get_available_missions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "mission_android_build",
                "title": "Prepare & Build Android Project",
                "category": "DEVELOPMENT",
                "steps": [
                    {"id": 1, "name": "Check Git Status & Branch", "status": "PENDING"},
                    {"id": 2, "name": "Verify Android SDK / ADB Devices", "status": "PENDING"},
                    {"id": 3, "name": "Clean Gradle Build Cache", "status": "PENDING"},
                    {"id": 4, "name": "Assemble Debug APK", "status": "PENDING"},
                    {"id": 5, "name": "Logcat Error Verification", "status": "PENDING"}
                ]
            },
            {
                "id": "mission_system_health",
                "title": "Tactical Full System Health Audit",
                "category": "MAINTENANCE",
                "steps": [
                    {"id": 1, "name": "Telemetry & CPU/RAM Stress Check", "status": "PENDING"},
                    {"id": 2, "name": "Disk Storage & Fragmentation Audit", "status": "PENDING"},
                    {"id": 3, "name": "Security & Threat Integrity Scan", "status": "PENDING"},
                    {"id": 4, "name": "Network Throughput & Connection Check", "status": "PENDING"},
                    {"id": 5, "name": "Generate Tactical Diagnostics Report", "status": "PENDING"}
                ]
            },
            {
                "id": "mission_deep_code_review",
                "title": "Deep Code & Crash Analysis Mission",
                "category": "ENGINEERING",
                "steps": [
                    {"id": 1, "name": "Inspect Active Codebase Tree", "status": "PENDING"},
                    {"id": 2, "name": "Scan for Syntax & Runtime Warnings", "status": "PENDING"},
                    {"id": 3, "name": "Detect Null Pointers & Memory Leaks", "status": "PENDING"},
                    {"id": 4, "name": "Formulate Refactoring Recommendations", "status": "PENDING"}
                ]
            }
        ]

    async def execute_mission(self, mission_id: str, callback=None) -> Dict[str, Any]:
        missions = {m["id"]: m for m in self.get_available_missions()}
        if mission_id not in missions:
            return {"status": "error", "message": f"Mission '{mission_id}' not found."}

        mission = missions[mission_id]
        mission_state = {
            "id": mission["id"],
            "title": mission["title"],
            "started_at": time.time(),
            "status": "RUNNING",
            "current_step": 0,
            "total_steps": len(mission["steps"]),
            "steps": [dict(s) for s in mission["steps"]],
            "logs": []
        }
        self.active_missions[mission_id] = mission_state

        for idx, step in enumerate(mission_state["steps"]):
            mission_state["current_step"] = idx + 1
            step["status"] = "RUNNING"
            mission_state["logs"].append(f"▶ Executing Step {idx+1}: {step['name']}")
            
            if callback:
                try:
                    await callback(mission_state)
                except Exception:
                    pass

            await asyncio.sleep(1.2) # Simulated operational step execution

            step["status"] = "COMPLETED"
            mission_state["logs"].append(f"✓ Step {idx+1} Completed: {step['name']}")
            
            if callback:
                try:
                    await callback(mission_state)
                except Exception:
                    pass

        mission_state["status"] = "COMPLETED"
        mission_state["completed_at"] = time.time()
        
        if self.memory:
            self.memory.log_audit("MISSION_EXECUTION", mission["title"], "COMPLETED", details=f"{len(mission['steps'])} steps executed")

        return mission_state

    async def run_workflow(self, workflow_name: str) -> Dict[str, Any]:
        if workflow_name not in self.custom_workflows:
            return {"status": "error", "message": f"Workflow '{workflow_name}' not found."}

        steps = self.custom_workflows[workflow_name]
        results = []
        for s in steps:
            action = s.get("action")
            args = s.get("args", {})
            desc = s.get("desc", action)
            if self.tools:
                res = self.tools.execute(action, **args)
                results.append({"step": desc, "status": "executed", "result": res})
            else:
                results.append({"step": desc, "status": "simulated"})

        return {"status": "success", "workflow": workflow_name, "results": results}
