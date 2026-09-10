import subprocess
import shutil
import os
import re
from typing import Dict, Any, List, Optional

class DeveloperAndAndroidCore:
    """Developer intelligence suite and Android ADB control center for Tony AI."""

    def __init__(self, memory=None):
        self.memory = memory

    # --- Android & ADB Tools ---
    def check_adb_installed(self) -> bool:
        return shutil.which("adb") is not None

    def list_adb_devices(self) -> Dict[str, Any]:
        if not self.check_adb_installed():
            return {
                "status": "warning",
                "adb_installed": False,
                "devices": [],
                "message": "ADB binary not detected on PATH. Virtual mock interface active."
            }
        try:
            out = subprocess.check_output(["adb", "devices"], text=True, stderr=subprocess.STDOUT, timeout=5)
            lines = [line.strip() for line in out.strip().split("\n")[1:] if line.strip()]
            devices = []
            for l in lines:
                parts = l.split()
                if len(parts) >= 2:
                    devices.append({"id": parts[0], "status": parts[1]})
            return {"status": "success", "adb_installed": True, "devices": devices}
        except Exception as e:
            return {"status": "error", "error": str(e), "devices": []}

    def get_logcat_errors(self, max_lines: int = 40) -> Dict[str, Any]:
        if not self.check_adb_installed():
            return {
                "status": "mock",
                "errors": [
                    "E/AndroidRuntime: FATAL EXCEPTION: main",
                    "E/AndroidRuntime: Process: com.stark.tony, PID: 12480",
                    "E/AndroidRuntime: java.lang.NullPointerException: Attempt to invoke virtual method on a null object reference",
                    "E/AndroidRuntime:   at com.stark.tony.MainActivity.onCreate(MainActivity.java:184)"
                ],
                "message": "Simulated logcat error stream (ADB not locally connected)."
            }
        try:
            cmd = ["adb", "logcat", "-d", "*:E"]
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=6)
            lines = out.strip().split("\n")[-max_lines:]
            return {"status": "success", "errors": lines}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_adb_shell(self, command: str) -> Dict[str, Any]:
        if not self.check_adb_installed():
            return {"status": "error", "error": "ADB is not available on host system."}
        try:
            cmd = ["adb", "shell", command]
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=10)
            return {"status": "success", "output": out}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # --- Git & Codebase Tools ---
    def git_status(self) -> Dict[str, Any]:
        try:
            out = subprocess.check_output(["git", "status", "-s"], text=True, stderr=subprocess.STDOUT, timeout=5)
            branch = subprocess.check_output(["git", "branch", "--show-current"], text=True, stderr=subprocess.STDOUT, timeout=5).strip()
            return {
                "status": "success",
                "branch": branch,
                "modified_files": [l.strip() for l in out.strip().split("\n") if l.strip()]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def git_recent_commits(self, count: int = 5) -> Dict[str, Any]:
        try:
            out = subprocess.check_output(["git", "log", f"-n{count}", "--oneline"], text=True, stderr=subprocess.STDOUT, timeout=5)
            commits = [l.strip() for l in out.strip().split("\n") if l.strip()]
            return {"status": "success", "commits": commits}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # --- Crash & Stack Trace Intelligence ---
    def analyze_crash_log(self, log_text: str) -> Dict[str, Any]:
        """Analyzes a raw crash log or stack trace and produces actionable debugging insights."""
        analysis = {
            "exception_type": "Unknown Exception",
            "culprit_file": "Unknown File",
            "line_number": None,
            "root_cause": "Unidentified stack anomaly",
            "suggested_fix": "Inspect log traces for variable initializations and null checks."
        }

        # Check for NullPointerException
        if "NullPointerException" in log_text:
            analysis["exception_type"] = "NullPointerException (NPE)"
            analysis["root_cause"] = "Attempted to invoke a method or access a field on a null object reference."
            analysis["suggested_fix"] = "Add null-safety assertions, initialize the target instance before invocation, or use Optional / safe-call operators (?.)."

        # Check for OutOfMemory
        elif "OutOfMemoryError" in log_text or "OOM" in log_text:
            analysis["exception_type"] = "OutOfMemoryError (OOM)"
            analysis["root_cause"] = "Heap allocation exceeded maximum allowed memory limits."
            analysis["suggested_fix"] = "Recycle large bitmaps, avoid retain cycles in static singletons, and leverage heap profiling."

        # Check for ClassNotFound / NoClassDefFound
        elif "ClassNotFoundException" in log_text or "NoClassDefFoundError" in log_text:
            analysis["exception_type"] = "Dependency Resolution Failure"
            analysis["root_cause"] = "Required class bytecode missing at runtime."
            analysis["suggested_fix"] = "Verify Gradle / Maven dependencies, ProGuard / R8 keep rules, and classpath inclusion."

        # Extract file and line
        file_match = re.search(r'at\s+[\w\.]+\.([\w]+\.[\w]+):(\d+)', log_text)
        if file_match:
            analysis["culprit_file"] = file_match.group(1)
            analysis["line_number"] = int(file_match.group(2))

        return analysis
