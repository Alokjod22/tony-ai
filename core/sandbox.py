import sys
import subprocess
import tempfile
import time
import os
import traceback
from typing import Dict, Any, Optional

class CodeSandboxEngine:
    """Stark Code Execution Sandbox with automatic exception analysis and self-healing loop."""

    def __init__(self, timeout_sec: int = 15):
        self.timeout_sec = timeout_sec

    def execute_python(self, code: str) -> Dict[str, Any]:
        """Executes a Python code snippet in a dedicated subprocess and captures stdout/stderr."""
        start_time = time.time()
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name

            # Run Python script
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            elapsed = round((time.time() - start_time) * 1000, 2)
            is_success = (result.returncode == 0)

            return {
                "success": is_success,
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
                "returncode": result.returncode,
                "execution_time_ms": elapsed,
                "code": code
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout_sec} seconds.",
                "returncode": -1,
                "execution_time_ms": self.timeout_sec * 1000,
                "code": code
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Sandbox execution error: {str(e)}\n{traceback.format_exc()}",
                "returncode": -1,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "code": code
            }
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

    def self_heal_and_execute(self, code: str, brain_ref: Any = None, max_attempts: int = 2) -> Dict[str, Any]:
        """Executes code. If it fails, asks the AI brain to diagnose and fix the error, then re-runs."""
        history = []
        current_code = code

        for attempt in range(1, max_attempts + 1):
            exec_res = self.execute_python(current_code)
            history.append({
                "attempt": attempt,
                "code": current_code,
                "result": exec_res
            })

            if exec_res["success"]:
                return {
                    "success": True,
                    "final_code": current_code,
                    "final_output": exec_res["stdout"],
                    "attempts": attempt,
                    "history": history,
                    "healed": (attempt > 1)
                }

            # If it failed and we have attempts remaining, invoke AI self-healing
            if attempt < max_attempts and brain_ref:
                heal_prompt = f"""You are the STARK SELF-HEALING CODE ENGINE.
The following Python script failed during execution:

```python
{current_code}
```

Error Output:
{exec_res['stderr']}

Please diagnose the exact cause of the failure and output ONLY the corrected Python code enclosed inside a ```python ... ``` block. Do not include extra conversational text."""
                try:
                    healed_resp = brain_ref.generate_raw_text(heal_prompt)
                    import re
                    match = re.search(r'```python\s*(.*?)\s*```', healed_resp, re.DOTALL)
                    if match:
                        current_code = match.group(1).strip()
                    else:
                        current_code = healed_resp.strip()
                except Exception:
                    break

        return {
            "success": False,
            "final_code": current_code,
            "final_output": exec_res.get("stderr", "Unknown error"),
            "attempts": len(history),
            "history": history,
            "healed": False
        }
