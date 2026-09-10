import re
from typing import Dict, Any

class IntentRouter:
    """High-speed heuristic and pattern classifier for routing user prompts."""

    INTENTS = [
        "SYSTEM_DIAGNOSTICS",
        "COMPUTER_CONTROL",
        "ANDROID_CORE",
        "DEVELOPER_CORE",
        "VISION_OCR",
        "AUTOMATION_WORKFLOW",
        "MEMORY_QUERY",
        "RESEARCH_CODEX",
        "CONVERSATION"
    ]

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        t = text.lower().strip()

        # 1. Vision & Screen Analysis
        if any(w in t for w in ["what's on my screen", "look at my screen", "read my screen", "screen scan", "analyze screen", "take screenshot", "ocr", "visible error", "read this error", "on the screen"]):
            return {
                "intent": "VISION_OCR",
                "confidence": 0.95,
                "handler": "vision_core"
            }

        # 2. Memory & Facts
        if any(w in t for w in ["what do you remember", "remember that", "remember this", "don't forget", "my preference", "forget about", "delete memory", "export memory", "show memories", "who am i", "my project"]):
            return {
                "intent": "MEMORY_QUERY",
                "confidence": 0.92,
                "handler": "memory_core"
            }

        # 3. Android & ADB
        if any(w in t for w in ["adb", "logcat", "android device", "install apk", "connect to phone", "android studio", "dumpsys", "package manager", "phone screen", "ndk"]):
            return {
                "intent": "ANDROID_CORE",
                "confidence": 0.94,
                "handler": "android_core"
            }

        # 4. Developer, Git & Crash Analysis
        if any(w in t for w in ["git status", "git diff", "git commit", "analyze crash", "stack trace", "nullpointerexception", "debug this", "fix this error", "refactor code", "write a function", "terminal command", "run build", "c++ function", "python script"]):
            return {
                "intent": "DEVELOPER_CORE",
                "confidence": 0.90,
                "handler": "developer_core"
            }

        # 5. Workflows & Missions
        if any(w in t for w in ["start development", "run workflow", "execute mission", "start mission", "automation", "clean workspace", "macro", "morning routine", "prepare build"]):
            return {
                "intent": "AUTOMATION_WORKFLOW",
                "confidence": 0.93,
                "handler": "workflow_engine"
            }

        # 6. Deep Research
        if any(w in t for w in ["deep research", "research on", "compare sources", "analyze literature", "cite sources", "investigate", "comprehensive analysis"]):
            return {
                "intent": "RESEARCH_CODEX",
                "confidence": 0.88,
                "handler": "research_engine"
            }

        # 7. System Diagnostics & Telemetry
        if any(w in t for w in ["cpu usage", "ram usage", "battery level", "why is my computer slow", "diagnostics", "telemetry", "system status", "hardware stats", "running processes", "kill process", "memory leak", "disk space"]):
            return {
                "intent": "SYSTEM_DIAGNOSTICS",
                "confidence": 0.95,
                "handler": "system_tools"
            }

        # 8. Computer & App Control
        if any(w in t for w in ["open ", "close ", "launch ", "type ", "search files", "move file", "create folder", "browse to", "navigate to", "open folder", "show folder"]):
            return {
                "intent": "COMPUTER_CONTROL",
                "confidence": 0.85,
                "handler": "computer_control"
            }

        # 9. General Conversation & Intelligence
        return {
            "intent": "CONVERSATION",
            "confidence": 0.80,
            "handler": "cognitive_llm"
        }
