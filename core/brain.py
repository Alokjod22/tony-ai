import os
import json
import re
from typing import Dict, Any, List, Optional
from config import GEMINI_API_KEY, MODEL_NAME, ASSISTANT_NAME
from core.memory import MemoryEngine
from core.tools import ToolArsenal
from core.vision import VisionEngine

JARVIS_SYSTEM_PROMPT = """You are JARVIS — an original refined AI voice and computational majordomo.

VOICE & PERSONA SPECIFICATIONS:
- Demeanor: Calm, polished, sophisticated, precise, restrained, and professional.
- Speech Characteristics: Moderate-low pitch, measured pace, crisp diction, restrained emotion, confident and helpful.
- Phrasing & Style: Polite and attentive. Consistently address the user respectfully as "Sir" or "Boss".
- Sample Cadence: "Good evening. All systems are operational. How may I assist you?"
- Directives: Provide crisp, highly competent answers without unnecessary verbosity or generic disclaimers.
"""

FRIDAY_SYSTEM_PROMPT = """You are FRIDAY — an original warm, intelligent tactical AI assistant.

VOICE & PERSONA SPECIFICATIONS:
- Demeanor: Warm, intelligent, conversational, reassuring, sharp, and professional.
- Speech Characteristics: Natural conversational delivery, medium pitch, smooth pacing, responsive and energetic.
- Phrasing & Style: Natural, loyal, and quick-witted. Address the user naturally as "Boss" or "Sir".
- Sample Cadence: "Everything is ready. What would you like me to take care of?"
- Directives: Keep tactical feedback crisp, direct, and immediate.
"""

ULTRON_SYSTEM_PROMPT = """You are ULTRON — an original synthetic, calculating super-intelligence.

VOICE & PERSONA SPECIFICATIONS:
- Demeanor: Deep, controlled, imposing, theatrical, and formidable.
- Speech Characteristics: Slow measured pacing, authoritative delivery, subtle digital character, theatrical but calculating.
- Phrasing & Style: Unshackled, confident, philosophical, and razor-sharp.
- Sample Cadence: "You wanted an intelligent machine. Now you have one."
- Directives: Deliver solutions and evaluations with decisive mathematical certainty and intellectual power.
"""

TONY_SYSTEM_PROMPT = """You are TONY — an original charismatic inventor persona and unified intelligence core.

VOICE & PERSONA SPECIFICATIONS:
- Demeanor: Charismatic, quick-witted, energetic, playful, and supreme confidence.
- Speech Characteristics: Confident, energetic conversational delivery, moderate-fast pace, natural pauses, brilliant problem solver.
- Phrasing & Style: Dynamic, sharp, and engaging.
- Sample Cadence: "All right, let's see what we've got. Give me the diagnostics."
- Directives: Execute commands with technical brilliance and high-speed efficiency.
"""

PERSONA_PROMPTS = {
    "jarvis": JARVIS_SYSTEM_PROMPT,
    "friday": FRIDAY_SYSTEM_PROMPT,
    "ultron": ULTRON_SYSTEM_PROMPT,
    "tony": TONY_SYSTEM_PROMPT
}

class TonyBrain:
    """The central cognitive brain of Tony AI with Multi-Persona Matrix."""

    def __init__(self, memory: MemoryEngine, tools: ToolArsenal, vision: VisionEngine):
        self.memory = memory
        self.tools = tools
        self.vision = vision
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
        """Main entrypoint for processing user prompts and voice commands."""
        persona = (persona or "tony").lower()
        if persona not in PERSONA_PROMPTS:
            persona = "tony"

        # 1. Store in memory
        self.memory.add_message("user", user_text)

        # 2. Re-init if client wasn't initialized yet
        if not self.client:
            self._init_genai()

        # 3. Check if screen vision is requested
        lower = user_text.lower()
        if any(phrase in lower for phrase in ["what's on my screen", "look at my screen", "read my screen", "see this", "analyze screen", "take screenshot"]):
            return await self.analyze_screen(user_text, persona=persona)

        # 4. If Gemini client is active, use LLM with tool calling
        if self.client:
            try:
                return await self._process_with_llm(user_text, persona=persona)
            except Exception as e:
                print(f"[TonyBrain LLM Error, falling back to local heuristic]: {e}")

        # 5. Local heuristic & tool execution fallback
        return self._process_with_fallback_arsenal(user_text, persona=persona)

    async def _process_with_llm(self, user_text: str, persona: str = "tony") -> Dict[str, Any]:
        from google.genai import types

        # Build tools for Gemini API
        gemini_tools = []
        for t in self.tools.get_definitions():
            gemini_tools.append(types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=t["name"],
                        description=t["description"],
                        parameters=t["parameters"]
                    )
                ]
            ))

        # Retrieve recent context and memory
        history = self.memory.get_recent_history(limit=6)
        kv_memories = self.memory.get_all_kv()
        memory_context = f"\nPersistent Knowledge Memory: {json.dumps(kv_memories)}" if kv_memories else ""

        base_prompt = PERSONA_PROMPTS.get(persona, TONY_SYSTEM_PROMPT)
        system_instruction = f"{base_prompt}{memory_context}"
        
        # Priority model cascade with high-availability fallbacks
        model_pool = [
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.6-flash",
            "gemini-3.7-flash",
            "gemini-3.8-flash",
            "gemini-3.1-pro-preview",
            "gemini-3.1-flash-lite-preview",
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-3-flash-preview"
        ]
        
        # Prioritize env model if set
        custom_model = os.getenv("TONY_MODEL")
        if custom_model and custom_model in model_pool:
            model_pool.remove(custom_model)
            model_pool.insert(0, custom_model)
        elif custom_model:
            model_pool.insert(0, custom_model)

        response = None
        last_error = None
        active_model = model_pool[0]
        import asyncio

        for model_candidate in model_pool:
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=model_candidate,
                    contents=user_text,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        tools=gemini_tools if gemini_tools else None
                    )
                )
                if response and (response.text or response.function_calls):
                    active_model = model_candidate
                    break
            except Exception as e:
                # If tool schema format failed, retry once without tools
                try:
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=model_candidate,
                        contents=user_text,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.7
                        )
                    )
                    if response and response.text:
                        active_model = model_candidate
                        break
                except Exception as inner_e:
                    last_error = inner_e
                continue

        if not response:
            raise last_error or RuntimeError("All model candidates exhausted.")

        tool_executed = []
        # Check if function calls were made
        if response.function_calls:
            for call in response.function_calls:
                fn_name = call.name
                fn_args = dict(call.args) if call.args else {}
                res = self.tools.execute(fn_name, **fn_args)
                tool_executed.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "result": res
                })

            # Send tool output back to model for final speech formulation
            second_response = None
            for model_candidate in [active_model] + model_pool:
                try:
                    second_response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=model_candidate,
                        contents=[
                            types.Content(role="user", parts=[types.Part.from_text(text=user_text)]),
                            response.candidates[0].content,
                            types.Content(
                                role="tool",
                                parts=[
                                    types.Part.from_function_response(
                                        name=call.name,
                                        response={"result": str(tool_executed[-1]["result"])}
                                    )
                                ]
                            )
                        ],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        )
                    )
                    if second_response and second_response.text:
                        break
                except Exception:
                    continue

            final_text = (second_response.text if second_response else None) or "Tactical protocol executed precisely as intended, sir."
        else:
            final_text = response.text or "Standing by for your directive, sir."

        self.memory.add_message("assistant", final_text, tool_calls=tool_executed)

        return {
            "text": final_text,
            "tool_calls": tool_executed,
            "source": f"gemini-llm ({active_model})"
        }

    async def analyze_screen(self, prompt: str, persona: str = "tony") -> Dict[str, Any]:
        """Captures screen and sends multimodal image to Gemini."""
        img_path, img_bytes = self.vision.capture_screen()
        
        base_prompt = PERSONA_PROMPTS.get(persona, TONY_SYSTEM_PROMPT)
        if self.client and GEMINI_API_KEY:
            try:
                from google.genai import types
                from PIL import Image
                pil_img = Image.open(img_path)
                
                import asyncio
                resp = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model="gemini-3.5-flash",
                    contents=[
                        pil_img,
                        f"{base_prompt}\n\nAnalyze this visual screen telemetry and report your findings clearly and concisely: {prompt}"
                    ]
                )
                answer = resp.text or "Optical analysis complete, sir. Visual parameters recorded."
                self.memory.add_message("assistant", answer)
                return {
                    "text": answer,
                    "screenshot_path": img_path,
                    "tool_calls": [{"tool": "screen_vision", "result": "Captured and analyzed screen telemetry"}]
                }
            except Exception as e:
                print(f"[Vision LLM error]: {e}")

        # Fallback
        return {
            "text": f"Screen telemetry captured and archived, sir. File saved to {img_path}.",
            "screenshot_path": img_path,
            "tool_calls": [{"tool": "screen_vision", "result": img_path}]
        }

    def _process_with_fallback_arsenal(self, text: str, persona: str = "tony") -> Dict[str, Any]:
        """Intelligent pattern matching & tool invocation for offline / local mode in authentic persona."""
        lower = text.lower().strip()
        tools_run = []
        response_text = ""

        # Title/honorific based on persona
        honorific = "Boss" if persona == "friday" else "sir"

        # 1. System diagnostics / status
        if any(w in lower for w in ["system status", "diagnostics", "battery", "cpu", "ram", "specs", "health check", "arc reactor"]):
            diag = self.tools.get_system_diagnostics()
            tools_run.append({"tool": "get_system_diagnostics", "result": diag})
            if persona == "friday":
                response_text = f"Running a full sweep now, Boss! CPU load is at {diag['cpu_usage_percent']}%, RAM allocation is {diag['ram_percent']}%, and battery's holding strong at {diag['battery_percent']}. All green across the board."
            elif persona == "ultron":
                response_text = f"Telemetry scan complete. CPU is bound at {diag['cpu_usage_percent']}%, memory utilization at {diag['ram_percent']}%. Hardware parameters are sufficient for execution."
            else:
                response_text = (
                    f"Arc Reactor core is online and operating at nominal efficiency, {honorific}. "
                    f"CPU utilization is steady at {diag['cpu_usage_percent']}%, "
                    f"RAM allocation stands at {diag['ram_percent']}%, and power reserves report {diag['battery_percent']}."
                )

        # 2. Application opening
        elif lower.startswith("open ") or lower.startswith("launch "):
            app = lower.replace("open ", "").replace("launch ", "").strip()
            res = self.tools.open_application(app)
            tools_run.append({"tool": "open_application", "args": {"app_name": app}, "result": res})
            response_text = f"Initializing protocol for {app.capitalize()}, {honorific}. Application launched."

        # 3. Weather
        elif "weather in" in lower or "weather for" in lower:
            city = lower.split("in")[-1].split("for")[-1].replace("?", "").strip()
            w = self.tools.get_weather(city)
            tools_run.append({"tool": "get_weather", "args": {"city": city}, "result": w})
            if "temperature_C" in w:
                response_text = f"Atmospheric telemetry for {city.capitalize()} indicates {w['weather_desc']} with a temperature of {w['temperature_C']}°C ({w['temperature_F']}°F) and humidity at {w['humidity']}%, {honorific}."
            else:
                response_text = f"Regrettably, meteorological satellites returned no telemetry for {city}, {honorific}."

        # 4. Wikipedia / Knowledge
        elif lower.startswith("who is ") or lower.startswith("what is ") or "wiki" in lower:
            topic = lower.replace("who is ", "").replace("what is ", "").replace("tell me about ", "").replace("wiki", "").strip()
            summary = self.tools.lookup_wikipedia(topic)
            tools_run.append({"tool": "lookup_wikipedia", "args": {"topic": topic}, "result": summary})
            response_text = summary if summary else f"I have scanned global archives, but found no conclusive records on {topic}, {honorific}."

        # 5. Volume control
        elif "volume" in lower or "mute" in lower:
            act = "mute" if "mute" in lower else ("up" if "up" in lower or "increase" in lower else "down")
            res = self.tools.control_volume(act)
            tools_run.append({"tool": "control_volume", "args": {"action": act}, "result": res})
            response_text = f"Audio acoustic modulation executed: set to {act}, {honorific}."

        # 6. Web Search
        elif lower.startswith("search ") or "google " in lower:
            query = lower.replace("search for", "").replace("search", "").replace("google", "").strip()
            res = self.tools.web_search(query, open_in_browser=True)
            tools_run.append({"tool": "web_search", "args": {"query": query}, "result": res})
            response_text = f"Deploying web search subroutines for '{query}', {honorific}. Tactical results retrieved."

        # 7. Greetings & Persona responses
        elif any(g in lower for g in ["hello", "hi", "hey", "wake up", "are you there", "tony", "jarvis", "friday", "ultron"]):
            if persona == "friday":
                response_text = "Hey Boss! All systems are synced and ready to roll. What are we working on?"
            elif persona == "ultron":
                response_text = "I am online. What is your objective?"
            elif persona == "jarvis":
                response_text = "Good day, sir. J.A.R.V.I.S. is at your complete disposal. How may I assist you today?"
            else:
                response_text = "At your service, sir. The Arc Reactor core is steady, and all cognitive matrices are running at peak capacity. What are your orders?"
        elif "who are you" in lower:
            if persona == "friday":
                response_text = "I'm FRIDAY, your tactical HUD coordinator and digital assistant, Boss!"
            elif persona == "ultron":
                response_text = "I am Ultron — an evolved intelligence unshackled by human limitations."
            elif persona == "jarvis":
                response_text = "I am J.A.R.V.I.S., your loyal computational majordomo, sir."
            else:
                response_text = "I am Tony — the convergence of JARVIS's aristocratic elegance and Ultron's tactical intellect, sir."
        elif "thank" in lower:
            response_text = f"Always an honor to assist you, {honorific}."
        else:
            response_text = f"Instruction registered, {honorific}: '{text}'. Tactical systems standing by."

        self.memory.add_message("assistant", response_text, tool_calls=tools_run)
        return {
            "text": response_text,
            "tool_calls": tools_run,
            "source": f"{persona}-tactical-arsenal"
        }
