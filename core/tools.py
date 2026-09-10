import os
import sys
import psutil
import subprocess
import webbrowser
import urllib.parse
import requests
import json
import datetime
import platform
from typing import Dict, Any, Callable

class ToolArsenal:
    """Jarvis & Ultron combined capability suite."""

    def __init__(self, memory_engine=None):
        self.memory = memory_engine
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        self._registry[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "func": func
        }

    def get_definitions(self):
        """Returns JSON schema definitions for function calling."""
        defs = []
        for name, data in self._registry.items():
            defs.append({
                "name": data["name"],
                "description": data["description"],
                "parameters": data["parameters"]
            })
        return defs

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        if name not in self._registry:
            return {"error": f"Tool '{name}' not found in Tony's arsenal."}
        try:
            result = self._registry[name]["func"](**kwargs)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _register_default_tools(self):
        # 1. System Telemetry & Diagnostics
        self.register(
            name="get_system_diagnostics",
            description="Get real-time CPU, RAM, Battery, Disk, and OS diagnostic metrics.",
            parameters={"type": "object", "properties": {}},
            func=self.get_system_diagnostics
        )

        # 2. Launch Application
        self.register(
            name="open_application",
            description="Launch or open a desktop application (e.g., notepad, calculator, chrome, spotify, vscode, terminal).",
            parameters={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name or executable of the application"}
                },
                "required": ["app_name"]
            },
            func=self.open_application
        )

        # 3. Web Search & Browser Navigation
        self.register(
            name="web_search",
            description="Search the web using DuckDuckGo/Google and open results in browser if requested.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "open_in_browser": {"type": "boolean", "description": "Whether to open the browser tab"}
                },
                "required": ["query"]
            },
            func=self.web_search
        )

        # 4. Wikipedia Quick Intelligence
        self.register(
            name="lookup_wikipedia",
            description="Lookup a topic summary on Wikipedia.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic or person to search"}
                },
                "required": ["topic"]
            },
            func=self.lookup_wikipedia
        )

        # 5. Weather Information
        self.register(
            name="get_weather",
            description="Fetch current weather and forecast for any city.",
            parameters={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            },
            func=self.get_weather
        )

        # 6. Windows Media & Volume Control
        self.register(
            name="control_volume",
            description="Adjust or set system volume (mute, unmute, or percentage on Windows).",
            parameters={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["mute", "unmute", "up", "down", "max"], "description": "Volume action to perform"}
                },
                "required": ["action"]
            },
            func=self.control_volume
        )

        # 7. Safe Shell Command Execution (Ultron Protocol)
        self.register(
            name="run_terminal_command",
            description="Run a terminal/shell command on the host machine to automate tasks or inspect files.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"]
            },
            func=self.run_terminal_command
        )

        # 8. Memory Management
        self.register(
            name="remember_information",
            description="Store key personal details, user facts, or project preferences in Tony's persistent memory.",
            parameters={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Identifier key for the memory (e.g., user_name, preferred_ide, project_goal)"},
                    "value": {"type": "string", "description": "Content or details to store"}
                },
                "required": ["key", "value"]
            },
            func=self.remember_information
        )

        self.register(
            name="recall_memory",
            description="Retrieve stored knowledge from Tony's persistent memory.",
            parameters={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key to look up (leave blank for all)"}
                }
            },
            func=self.recall_memory
        )

        # 9. Task Management
        self.register(
            name="manage_tasks",
            description="Add or list reminders, action items, and tasks.",
            parameters={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["add", "list", "complete"], "description": "Task action"},
                    "task_text": {"type": "string", "description": "Description of the task (when adding)"},
                    "task_id": {"type": "integer", "description": "Task ID (when completing)"}
                },
                "required": ["action"]
            },
            func=self.manage_tasks
        )

    # --- Tool Implementations ---

    def get_system_diagnostics(self) -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        battery = psutil.sensors_battery()
        
        diag = {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_usage_percent": cpu_percent,
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_used_gb": round(mem.used / (1024**3), 2),
            "ram_total_gb": round(mem.total / (1024**3), 2),
            "ram_percent": mem.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "disk_percent": disk.percent,
            "battery_percent": battery.percent if battery else "N/A (Plugged In)",
            "power_plugged": battery.power_plugged if battery else True,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return diag

    def open_application(self, app_name: str) -> str:
        app_map = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "calculator": "calc.exe",
            "chrome": "chrome",
            "browser": "https://www.google.com",
            "edge": "msedge",
            "vscode": "code",
            "code": "code",
            "terminal": "wt.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
            "taskmgr": "taskmgr.exe",
            "task manager": "taskmgr.exe",
            "spotify": "spotify.exe",
            "youtube": "https://www.youtube.com"
        }
        target = app_map.get(app_name.lower().strip(), app_name)
        if target.startswith("http://") or target.startswith("https://"):
            webbrowser.open(target)
            return f"Opened {target} in default web browser."
        
        try:
            if platform.system() == "Windows":
                os.startfile(target)
            else:
                subprocess.Popen([target])
            return f"Successfully initiated {app_name}."
        except Exception as e:
            # Fallback to start command
            try:
                subprocess.Popen(f"start {target}", shell=True)
                return f"Launched {app_name} via Windows Shell."
            except Exception as e2:
                return f"Failed to open {app_name}: {e2}"

    def web_search(self, query: str, open_in_browser: bool = False) -> Dict[str, Any]:
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        if open_in_browser:
            webbrowser.open(url)
            return {"query": query, "url": url, "status": "Search opened in browser."}
        
        # Also query duckduckgo instant answer API for direct quick snippet
        try:
            api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json"
            resp = requests.get(api_url, timeout=5).json()
            abstract = resp.get("AbstractText") or resp.get("Heading") or ""
            return {
                "query": query,
                "url": url,
                "summary": abstract if abstract else f"Google search link ready for '{query}'"
            }
        except Exception:
            return {"query": query, "url": url}

    def lookup_wikipedia(self, topic: str) -> str:
        try:
            endpoint = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
            headers = {"User-Agent": "TonyAssistant/1.0 (tony@ai.local)"}
            r = requests.get(endpoint, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return data.get("extract", "No extract found.")
            return f"No direct Wikipedia article found for '{topic}'."
        except Exception as e:
            return f"Wikipedia lookup error: {e}"

    def get_weather(self, city: str) -> Dict[str, Any]:
        try:
            # wttr.in gives clean JSON weather
            url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
            r = requests.get(url, timeout=6)
            if r.status_code == 200:
                data = r.json()
                current = data["current_condition"][0]
                return {
                    "city": city,
                    "temperature_C": current.get("temp_C"),
                    "temperature_F": current.get("temp_F"),
                    "weather_desc": current.get("weatherDesc", [{}])[0].get("value"),
                    "humidity": current.get("humidity"),
                    "wind_speed_kmph": current.get("windspeedKmph"),
                    "feels_like_C": current.get("FeelsLikeC")
                }
            return {"error": f"Could not retrieve weather for {city}."}
        except Exception as e:
            return {"error": str(e)}

    def control_volume(self, action: str) -> str:
        if platform.system() != "Windows":
            return f"Volume control currently only configured for Windows."
        
        # Use NirCmd or powershell vbs key simulator for standard media keys
        key_map = {
            "mute": 0xAD,      # VK_VOLUME_MUTE
            "unmute": 0xAD,
            "down": 0xAE,      # VK_VOLUME_DOWN
            "up": 0xAF         # VK_VOLUME_UP
        }
        
        try:
            if action in ["up", "down", "mute", "unmute"]:
                times = 5 if action in ["up", "down"] else 1
                ps_script = f"""
                $obj = New-Object -ComObject WScript.Shell
                for ($i=0; $i -lt {times}; $i++) {{
                    $obj.SendKeys([char]174) # 174 is down, 175 is up, 173 is mute
                }}
                """
                if action == "up":
                    ps_cmd = f"$obj = New-Object -ComObject WScript.Shell; for($i=0;$i -lt 5;$i++){{$obj.SendKeys([char]175)}}"
                elif action == "down":
                    ps_cmd = f"$obj = New-Object -ComObject WScript.Shell; for($i=0;$i -lt 5;$i++){{$obj.SendKeys([char]174)}}"
                else:
                    ps_cmd = f"$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]173)"
                
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
                return f"Volume {action} command dispatched."
            elif action == "max":
                ps_cmd = f"$obj = New-Object -ComObject WScript.Shell; for($i=0;$i -lt 50;$i++){{$obj.SendKeys([char]175)}}"
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
                return "Volume maximized."
        except Exception as e:
            return f"Volume error: {e}"
        return f"Volume action {action} performed."

    def run_terminal_command(self, command: str) -> Dict[str, Any]:
        # Disallow explicitly destructive commands
        dangerous = ["format ", "rmdir /s /q c:", "drop database", "del /f /s /q c:"]
        for d in dangerous:
            if d in command.lower():
                return {"error": f"Security restriction: Command contains forbidden pattern '{d}'."}
        
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "exit_code": proc.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command execution timed out after 15 seconds."}
        except Exception as e:
            return {"error": str(e)}

    def remember_information(self, key: str, value: str) -> str:
        if not self.memory:
            return "Memory engine not attached."
        self.memory.set(key, value)
        return f"Memory stored: '{key}' = '{value}'"

    def recall_memory(self, key: str = "") -> Any:
        if not self.memory:
            return "Memory engine not attached."
        if key:
            return self.memory.get(key, "No memory found for this key.")
        return self.memory.get_all_kv()

    def manage_tasks(self, action: str, task_text: str = "", task_id: int = 0) -> Any:
        if not self.memory:
            return "Memory engine not attached."
        if action == "add":
            if not task_text:
                return "Task text is required."
            tid = self.memory.add_task(task_text)
            return f"Task #{tid} added: '{task_text}'"
        elif action == "list":
            return self.memory.list_tasks()
        elif action == "complete":
            self.memory.complete_task(task_id)
            return f"Task #{task_id} marked as completed."
        return "Invalid action."
