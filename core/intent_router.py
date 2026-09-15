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
        "DEEP_RESEARCH",
        "RUN_CODE",
        "SPAWN_SWARM",
        "QUERY_VAULT",
        "EXECUTE_ROUTINE",
        "IMAGE_GENERATION",
        "CONVERSATION"
    ]

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        t = text.lower().strip()

        # 1. Multi-Modal Hugging Face Image Generation
        if any(w in t for w in ["generate image", "create image", "draw ", "picture of", "render image", "generate photo", "flux image", "generate an image"]):
            return {
                "intent": "IMAGE_GENERATION",
                "confidence": 0.97,
                "handler": "huggingface_tools"
            }

        # 2. Code Sandbox & Script Execution
        if any(w in t for w in ["run python", "run this code", "execute python", "run code", "evaluate code", "execute script", "run snippet", "execute this code"]):
            return {
                "intent": "RUN_CODE",
                "confidence": 0.96,
                "handler": "code_sandbox"
            }

        # 3. Multi-Agent Swarm Dispatch
        if any(w in t for w in ["spawn swarm", "subagent swarm", "agent swarm", "dispatch agents", "multi-agent", "swarm analysis", "deploy swarm", "agent team"]):
            return {
                "intent": "SPAWN_SWARM",
                "confidence": 0.95,
                "handler": "agent_swarm"
            }

        # 4. Knowledge Vault & Document Search
        if any(w in t for w in ["search vault", "in my documents", "knowledge vault", "search documents", "ask document", "vault search", "query vault", "document search"]):
            return {
                "intent": "QUERY_VAULT",
                "confidence": 0.93,
                "handler": "knowledge_vault"
            }

        # 5. Protocols & Custom Routines
        if any(w in t for w in ["run protocol", "execute protocol", "protocol morning", "protocol dev", "protocol security", "start protocol", "protocol zero"]):
            return {
                "intent": "EXECUTE_ROUTINE",
                "confidence": 0.94,
                "handler": "protocol_engine"
            }

        # 6. Vision & Screen Analysis
        if any(w in t for w in ["what's on my screen", "look at my screen", "read my screen", "screen scan", "analyze screen", "take screenshot", "ocr", "visible error", "read this error", "on the screen"]):
            return {
                "intent": "VISION_OCR",
                "confidence": 0.95,
                "handler": "vision_core"
            }

        # 7. Memory & Facts
        if any(w in t for w in ["what do you remember", "remember that", "remember this", "don't forget", "my preference", "forget about", "delete memory", "export memory", "show memories", "who am i", "my project"]):
            return {
                "intent": "MEMORY_QUERY",
                "confidence": 0.92,
                "handler": "memory_core"
            }

        # 8. Android & ADB
        if any(w in t for w in ["adb", "logcat", "android device", "install apk", "connect to phone", "android studio", "dumpsys", "package manager", "phone screen", "ndk"]):
            return {
                "intent": "ANDROID_CORE",
                "confidence": 0.94,
                "handler": "android_core"
            }

        # 9. Developer, Git & Crash Analysis
        if any(w in t for w in ["git status", "git diff", "git commit", "analyze crash", "stack trace", "nullpointerexception", "debug this", "fix this error", "refactor code", "write a function", "terminal command", "run build", "c++ function"]):
            return {
                "intent": "DEVELOPER_CORE",
                "confidence": 0.90,
                "handler": "developer_core"
            }

        # 10. Workflows & Missions
        if any(w in t for w in ["start development", "run workflow", "execute mission", "start mission", "clean workspace", "prepare build"]):
            return {
                "intent": "AUTOMATION_WORKFLOW",
                "confidence": 0.93,
                "handler": "workflow_engine"
            }

        # 11. Deep Research
        if any(w in t for w in ["deep research", "research on", "compare sources", "analyze literature", "cite sources", "investigate", "comprehensive analysis"]):
            return {
                "intent": "DEEP_RESEARCH",
                "confidence": 0.88,
                "handler": "research_engine"
            }

        # 12. System Diagnostics & Telemetry
        if any(w in t for w in ["cpu usage", "ram usage", "battery level", "why is my computer slow", "diagnostics", "telemetry", "system status", "hardware stats", "running processes", "kill process", "memory leak", "disk space"]):
            return {
                "intent": "SYSTEM_DIAGNOSTICS",
                "confidence": 0.95,
                "handler": "system_tools"
            }

        # 13. Computer & App Control
        if any(w in t for w in ["open ", "close ", "launch ", "type ", "search files", "move file", "create folder", "browse to", "navigate to", "open folder", "show folder"]):
            return {
                "intent": "COMPUTER_CONTROL",
                "confidence": 0.85,
                "handler": "computer_control"
            }

        # 14. General Conversation & Intelligence
        return {
            "intent": "CONVERSATION",
            "confidence": 0.80,
            "handler": "cognitive_llm"
        }
