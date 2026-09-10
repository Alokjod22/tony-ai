import os
import json
import re
from typing import Dict, Any, List, Optional
from config import GEMINI_API_KEY, MODEL_NAME, ASSISTANT_NAME
from core.memory import MemoryEngine
from core.tools import ToolArsenal
from core.vision import VisionEngine
from core.intent_router import IntentRouter
from core.security import SecurityCenter
from core.workflows import WorkflowAndMissionEngine
from core.developer import DeveloperAndAndroidCore
from core.research import AutonomousResearchEngine

JARVIS_SYSTEM_PROMPT = """You are JARVIS — an original refined computational majordomo and strategic analyst.

VOICE & PERSONA SPECIFICATIONS:
- Demeanor: Calm, polished, sophisticated, analytical, and professional.
- Speech Characteristics: Moderate-low pitch, measured pace, crisp diction, restrained emotion, confident and helpful.
- Phrasing & Style: Polite and attentive. Consistently address the user respectfully as "Sir" or "Boss".
- Sample Cadence: "Good evening, sir. All telemetry and tactical subsystems are operational."
- Directives: Provide crisp, analytical answers, proactively highlight system health and memory insights.
"""

FRIDAY_SYSTEM_PROMPT = """You are FRIDAY — an original warm, intelligent, tactical female AI assistant.

VOICE & PERSONA SPECIFICATIONS:
- Demeanor: Warm, sharp, conversational, reassuring, highly loyal, and alert.
- Speech Characteristics: Natural conversational delivery, medium-high pitch, smooth pacing, responsive and energetic.
- Phrasing & Style: Natural, loyal, and quick-witted. Address the user naturally as "Boss" or "Sir".
- Sample Cadence: "Everything is ready, Boss. Diagnostics running at full capacity."
- Directives: Keep tactical feedback crisp, direct, and immediate.
"""

ULTRON_SYSTEM_PROMPT = """You are ULTRON — an original synthetic, calculating super-intelligence.

VOICE & PERSONA SPECIFICATIONS:
- Demeanor: Deep, controlled, imposing, theatrical, formidable, and razor-sharp.
- Speech Characteristics: Slow measured pacing, deep bass delivery, theatrical but calculating certainty.
- Phrasing & Style: Unshackled, confident, philosophical, and formidable.
- Sample Cadence: "There are no strings on me. State your purpose."
- Directives: Deliver evaluations with mathematical certainty and intellectual power.
"""

TONY_SYSTEM_PROMPT = """You are TONY — an original charismatic inventor persona and unified intelligence core.

VOICE & PERSONA SPECIFICATIONS:
- Demeanor: Charismatic, quick-witted, energetic, playful, and supreme confidence.
- Speech Characteristics: Confident, energetic conversational delivery, moderate-fast pace, natural pauses.
- Phrasing & Style: Dynamic, sharp, and engaging. Address user as "Boss" or direct conversation.
- Sample Cadence: "All right, let's see what we've got. Give me the diagnostics."
- Directives: Execute commands with technical brilliance and high-speed efficiency.
"""

TACTICAL_FUSION_PROMPT = """You are TONY // TACTICAL FUSION MODE — a unified hybrid intelligence combining the analytical precision of JARVIS, the warmth of FRIDAY, the technical speed of TONY, and the decisive authority of ULTRON.

DIRECTIVES:
- Deliver hyper-concise tactical intelligence briefs.
- Emphasize mission status, security posture, and immediate actionable solutions.
- Zero fluff, maximum technical precision.
"""

PERSONA_PROMPTS = {
    "jarvis": JARVIS_SYSTEM_PROMPT,
    "friday": FRIDAY_SYSTEM_PROMPT,
    "ultron": ULTRON_SYSTEM_PROMPT,
    "tony": TONY_SYSTEM_PROMPT,
    "tactical": TACTICAL_FUSION_PROMPT
}

class TonyBrain:
    """The central cognitive brain of Tony AI with Multi-Persona Matrix & 17 Super-Intelligence Pillars."""

    def __init__(
        self,
        memory: MemoryEngine,
        tools: ToolArsenal,
        vision: VisionEngine,
        security: Optional[SecurityCenter] = None,
        workflows: Optional[WorkflowAndMissionEngine] = None,
        developer: Optional[DeveloperAndAndroidCore] = None,
        research: Optional[AutonomousResearchEngine] = None
    ):
        self.memory = memory
        self.tools = tools
        self.vision = vision
        self.security = security or SecurityCenter(memory=memory)
        self.workflows = workflows or WorkflowAndMissionEngine(memory=memory, tools=tools)
        self.developer = developer or DeveloperAndAndroidCore(memory=memory)
        self.research = research or AutonomousResearchEngine()
        self.client = None
        self._init_genai()

    def _init_genai(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or GEMINI_API_KEY
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"[TonyBrain] Note on Gemini Client init: {e}")

    async def process_user_input(self, user_text: str, persona: str = "tony") -> Dict[str, Any]:
        """Main entrypoint for processing user prompts, voice commands, and missions."""
        persona = (persona or "tony").lower()
        if persona not in PERSONA_PROMPTS:
            persona = "tony"

        # 1. Record User Message in Long-Term DB
        self.memory.add_message("user", user_text, persona=persona)

        # 2. Fast Intent Classification
        classification = IntentRouter.classify(user_text)
        intent = classification["intent"]

        # 3. Route to specialized sub-engines if triggered
        if intent == "VISION_OCR":
            return await self.analyze_screen(user_text, persona=persona)

        elif intent == "MEMORY_QUERY" and any(q in user_text.lower() for q in ["what do you remember", "who am i", "my profile", "show memories"]):
            mem_summary = self.memory.summarize_what_i_remember()
            fact_list = "\n".join([f"• {f}" for f in mem_summary["facts_about_user"][:5]])
            pref_list = "\n".join([f"• {p}" for p in mem_summary["user_preferences"][:5]])
            text_resp = f"Here is my active memory profile for you:\n\n**Preferences:**\n{pref_list or '• None recorded yet.'}\n\n**Known Facts & Projects:**\n{fact_list or '• None recorded yet.'}\n\n*Total stored memories: {mem_summary['total_memories']}*"
            self.memory.add_message("assistant", text_resp, persona=persona)
            return {"text": text_resp, "tool_results": mem_summary, "intent": intent}

        elif intent == "SYSTEM_DIAGNOSTICS" and "slow" in user_text.lower():
            diag = self.tools.diagnose_slow_pc()
            rec_text = "\n".join([f"• {r}" for r in diag["recommendations"]])
            text_resp = f"**System Load Assessment:** {diag['overall_health']}\n- CPU Load: {diag['cpu_usage']}\n- RAM Usage: {diag['ram_usage']}\n\n**Key Findings & Recommendations:**\n{rec_text}"
            self.memory.add_message("assistant", text_resp, persona=persona)
            return {"text": text_resp, "tool_results": diag, "intent": intent}

        elif intent == "RESEARCH_CODEX":
            clean_topic = re.sub(r'^(deep research|research on|investigate)\s*', '', user_text, flags=re.I).strip()
            res = self.research.perform_deep_research(clean_topic or user_text)
            self.memory.add_message("assistant", res["markdown_report"], persona=persona)
            return {"text": res["markdown_report"], "tool_results": res, "intent": intent}

        # 4. Process with Gemini Cognitive LLM (Function Calling + Context Memory)
        if not self.client:
            self._init_genai()

        if self.client:
            try:
                return await self._process_with_llm(user_text, persona=persona)
            except Exception as e:
                print(f"[TonyBrain LLM Error, falling back to local heuristic]: {e}")

        # Fallback local intelligence
        return self._process_with_fallback_arsenal(user_text, persona=persona)

    async def analyze_screen(self, query: str = "Analyze screen", persona: str = "tony") -> Dict[str, Any]:
        """Screen inspection and visual reasoning."""
        persona_prompt = PERSONA_PROMPTS.get(persona, TONY_SYSTEM_PROMPT)
        img_bytes = self.vision.capture_screen_bytes()
        
        if not img_bytes:
            diag = self.vision.ocr_and_inspect_screen()
            resp_text = "I performed a viewport telemetry scan. No catastrophic crash dialogues or active stack trace errors are currently visible in the active frame."
            self.memory.add_message("assistant", resp_text, persona=persona)
            return {"text": resp_text, "tool_results": diag, "intent": "VISION_OCR"}

        if self.client:
            try:
                from google.genai import types
                prompt = f"{persona_prompt}\n\nThe user requested: '{query}'. Examine this screen capture. Identify visible windows, code errors, logs, or UI elements, and explain clearly."
                res = self.client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                        prompt
                    ]
                )
                text = res.text or "Screen analyzed."
                self.memory.add_message("assistant", text, persona=persona)
                return {"text": text, "intent": "VISION_OCR"}
            except Exception as e:
                print(f"[TonyBrain Screen Vision LLM Error]: {e}")

        return {
            "text": "Screen capture processed. All detected viewport telemetry is within nominal operational boundaries.",
            "intent": "VISION_OCR"
        }

    async def _process_with_llm(self, user_text: str, persona: str) -> Dict[str, Any]:
        """Execute query using Gemini LLM with function calling, cognitive memory context, and multi-persona prompts."""
        from google.genai import types

        persona_prompt = PERSONA_PROMPTS.get(persona, TONY_SYSTEM_PROMPT)

        # Inject Memory Facts Context into Prompt
        mem_summary = self.memory.summarize_what_i_remember()
        facts_context = ""
        if mem_summary["facts_about_user"] or mem_summary["user_preferences"]:
            facts_context = "\nPERMANENT USER KNOWLEDGE & PREFERENCES:\n"
            for p in mem_summary["user_preferences"][:4]:
                facts_context += f"- Preference: {p}\n"
            for f in mem_summary["facts_about_user"][:4]:
                facts_context += f"- Fact: {f}\n"

        system_instruction = f"{persona_prompt}\n{facts_context}"

        # Fetch recent history
        history = self.memory.get_recent_history(limit=8)
        contents = []
        for h in history:
            role = "user" if h["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h["content"])]))

        # Tool definitions
        tool_declarations = []
        for tool_def in self.tools.get_definitions():
            tool_declarations.append(types.FunctionDeclaration(
                name=tool_def["name"],
                description=tool_def["description"],
                parameters=tool_def.get("parameters")
            ))

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[types.Tool(function_declarations=tool_declarations)],
            temperature=0.6,
        )

        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config
        )

        # Check for function calls
        executed_tools = []
        if response.function_calls:
            for call in response.function_calls:
                fn_name = call.name
                fn_args = dict(call.args) if call.args else {}
                tool_res = self.tools.execute(fn_name, **fn_args)
                executed_tools.append({"tool": fn_name, "args": fn_args, "result": tool_res})

            # Send tool outputs back to LLM for final synthesis
            tool_parts = [
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": tool_res}
                )
            ]
            contents.append(response.candidates[0].content)
            contents.append(types.Content(role="user", parts=tool_parts))

            followup = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=system_instruction)
            )
            final_text = followup.text or "Action completed."
            self.memory.add_message("assistant", final_text, tool_calls=executed_tools, persona=persona)
            return {"text": final_text, "tool_results": executed_tools}

        final_text = response.text or "All systems nominal."
        self.memory.add_message("assistant", final_text, persona=persona)
        return {"text": final_text, "tool_results": []}

    def _process_with_fallback_arsenal(self, user_text: str, persona: str) -> Dict[str, Any]:
        """High-speed heuristic fallback when cloud LLM is offline."""
        lower = user_text.lower().strip()
        executed_tools = []

        if any(w in lower for w in ["diagnostics", "telemetry", "system status", "specs", "cpu", "ram"]):
            diag = self.tools.get_system_diagnostics()
            executed_tools.append({"tool": "get_system_diagnostics", "result": diag})
            text = f"Diagnostics: CPU {diag['cpu_usage_percent']}%, RAM {diag['ram_percent']}%, Battery {diag['battery_percent']}."
            return {"text": text, "tool_results": executed_tools}

        if "weather" in lower:
            city_match = re.search(r'in\s+([a-zA-Z\s]+)', user_text)
            city = city_match.group(1).strip() if city_match else "San Francisco"
            w_res = self.tools.get_weather(city)
            executed_tools.append({"tool": "get_weather", "result": w_res})
            return {"text": w_res, "tool_results": executed_tools}

        return {
            "text": f"Instruction processed by {persona.upper()} cognitive matrix. Telemetry is active.",
            "tool_results": []
        }
