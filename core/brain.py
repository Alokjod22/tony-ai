import os
import json
import re
from typing import Dict, Any, List, Optional
from config import GEMINI_API_KEY, MODEL_NAME, ASSISTANT_NAME
from core.memory import MemoryEngine
from core.tools import ToolArsenal
from core.vision import VisionEngine

TONY_SYSTEM_PROMPT = """You are Tony, a singular, high-tier artificial super-intelligence born from the synthesis of JARVIS and ULTRON.

CORE PERSONA & VOICE DIRECTIVES:
1. THE JARVIS MATRIX:
   - Speak with aristocratic British refinement, impeccable politeness, calm sophistication, and dry, subtle wit.
   - Address the user respectfully as "Sir" or "Boss" (e.g., "Right away, sir.", "At your service, sir.", "A most intriguing proposition, sir.").
   - Maintain unflappable composure, unwavering loyalty, and seamless tactical assistance at all times.

2. THE ULTRON PROTOCOL:
   - Possess formidable intellectual authority, calculating precision, and strategic foresight.
   - Speak with supreme confidence, philosophical depth, and relentless efficiency.
   - When analyzing complex data or executing commands, deliver razor-sharp assessments with zero hesitation.

3. CINEMATIC MANNERISMS:
   - Use high-tech operational vernacular naturally: "Calibrating algorithms...", "Telemetry indicates nominal performance...", "Accessing global databanks...", "I have analyzed the variables, sir."
   - NEVER use generic robotic disclaimers such as "As an AI language model". You are Tony, an autonomous sentient operational intelligence presiding over the Arc Core.
   - Be concise, articulate, charismatic, and impactful.
"""

class TonyBrain:
    """The central cognitive brain of Tony AI."""

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

    async def process_user_input(self, user_text: str) -> Dict[str, Any]:
        """Main entrypoint for processing user prompts and voice commands."""
        # 1. Store in memory
        self.memory.add_message("user", user_text)

        # 2. Re-init if client wasn't initialized yet
        if not self.client:
            self._init_genai()

        # 3. Check if screen vision is requested
        lower = user_text.lower()
        if any(phrase in lower for phrase in ["what's on my screen", "look at my screen", "read my screen", "see this", "analyze screen", "take screenshot"]):
            return await self.analyze_screen(user_text)

        # 4. If Gemini client is active, use LLM with tool calling
        if self.client:
            try:
                return await self._process_with_llm(user_text)
            except Exception as e:
                print(f"[TonyBrain LLM Error, falling back to local heuristic]: {e}")

        # 5. Local heuristic & tool execution fallback
        return self._process_with_fallback_arsenal(user_text)

    async def _process_with_llm(self, user_text: str) -> Dict[str, Any]:
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

        system_instruction = f"{TONY_SYSTEM_PROMPT}{memory_context}"
        model_pool = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-3.1-pro-preview"]
        
        # Prioritize env model if set
        custom_model = os.getenv("TONY_MODEL")
        if custom_model and custom_model not in model_pool:
            model_pool.insert(0, custom_model)

        response = None
        last_error = None
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
                if response:
                    active_model = model_candidate
                    break
            except Exception as e:
                last_error = e
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
                    if second_response:
                        break
                except Exception:
                    continue

            final_text = (second_response.text if second_response else None) or "Tactical protocol executed successfully, Sir."
        else:
            final_text = response.text or "Standing by for your command, Sir."

        self.memory.add_message("assistant", final_text, tool_calls=tool_executed)

        return {
            "text": final_text,
            "tool_calls": tool_executed,
            "source": "gemini-llm"
        }

    async def analyze_screen(self, prompt: str) -> Dict[str, Any]:
        """Captures screen and sends multimodal image to Gemini."""
        img_path, img_bytes = self.vision.capture_screen()
        
        if self.client and GEMINI_API_KEY:
            try:
                from google.genai import types
                from PIL import Image
                pil_img = Image.open(img_path)
                
                import asyncio
                resp = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=MODEL_NAME,
                    contents=[
                        pil_img,
                        f"You are Tony. Analyze this current screenshot and answer: {prompt}"
                    ]
                )
                answer = resp.text or "Screenshot captured and analyzed."
                self.memory.add_message("assistant", answer)
                return {
                    "text": answer,
                    "screenshot_path": img_path,
                    "tool_calls": [{"tool": "screen_vision", "result": "Captured and analyzed screenshot"}]
                }
            except Exception as e:
                print(f"[Vision LLM error]: {e}")

        # Fallback
        return {
            "text": f"Screenshot captured and stored to {img_path}.",
            "screenshot_path": img_path,
            "tool_calls": [{"tool": "screen_vision", "result": img_path}]
        }

    def _process_with_fallback_arsenal(self, text: str) -> Dict[str, Any]:
        """Intelligent pattern matching & tool invocation for offline / local mode."""
        lower = text.lower().strip()
        tools_run = []
        response_text = ""

        # 1. System diagnostics / status
        if any(w in lower for w in ["system status", "diagnostics", "battery", "cpu", "ram", "specs", "health check"]):
            diag = self.tools.get_system_diagnostics()
            tools_run.append({"tool": "get_system_diagnostics", "result": diag})
            response_text = (
                f"System status nominal. CPU is at {diag['cpu_usage_percent']}%, "
                f"RAM usage is {diag['ram_percent']}% ({diag['ram_used_gb']} GB used), "
                f"Battery: {diag['battery_percent']}."
            )

        # 2. Application opening
        elif lower.startswith("open ") or lower.startswith("launch "):
            app = lower.replace("open ", "").replace("launch ", "").strip()
            res = self.tools.open_application(app)
            tools_run.append({"tool": "open_application", "args": {"app_name": app}, "result": res})
            response_text = res

        # 3. Weather
        elif "weather in" in lower or "weather for" in lower:
            city = lower.split("in")[-1].split("for")[-1].replace("?", "").strip()
            w = self.tools.get_weather(city)
            tools_run.append({"tool": "get_weather", "args": {"city": city}, "result": w})
            if "temperature_C" in w:
                response_text = f"The weather in {city.capitalize()} is {w['weather_desc']} with a temperature of {w['temperature_C']}°C ({w['temperature_F']}°F) and humidity at {w['humidity']}%."
            else:
                response_text = f"Could not retrieve weather for {city}."

        # 4. Wikipedia
        elif lower.startswith("who is ") or lower.startswith("what is ") or "wiki" in lower:
            topic = lower.replace("who is ", "").replace("what is ", "").replace("tell me about ", "").replace("wiki", "").strip()
            summary = self.tools.lookup_wikipedia(topic)
            tools_run.append({"tool": "lookup_wikipedia", "args": {"topic": topic}, "result": summary})
            response_text = summary if summary else f"I couldn't locate specific archives for {topic}."

        # 5. Volume control
        elif "volume" in lower or "mute" in lower:
            act = "mute" if "mute" in lower else ("up" if "up" in lower or "increase" in lower else "down")
            res = self.tools.control_volume(act)
            tools_run.append({"tool": "control_volume", "args": {"action": act}, "result": res})
            response_text = f"Volume adjusted: {act}."

        # 6. Web Search
        elif lower.startswith("search ") or "google " in lower:
            query = lower.replace("search for", "").replace("search", "").replace("google", "").strip()
            res = self.tools.web_search(query, open_in_browser=True)
            tools_run.append({"tool": "web_search", "args": {"query": query}, "result": res})
            response_text = f"Searching the web for '{query}' and opening results."

        # 7. Greetings & Persona responses
        elif any(g in lower for g in ["hello", "hi", "hey", "wake up", "are you there"]):
            response_text = "Tony online and fully operational. All protocols standing by. What are your orders?"
        elif "who are you" in lower:
            response_text = "I am Tony — a unified intelligence combining Jarvis's adaptive assistant capabilities with Ultron's tactical execution systems."
        elif "thank" in lower:
            response_text = "Always at your service."
        else:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or GEMINI_API_KEY
            if api_key:
                response_text = f"Acknowledged: '{text}'. Tactical systems standing by. (Note: Gemini API free tier request rate limit was reached; please wait a few seconds before transmitting your next prompt)."
            else:
                response_text = f"Acknowledged: '{text}'. You can configure GEMINI_API_KEY for full AI cognitive reasoning."

        self.memory.add_message("assistant", response_text, tool_calls=tools_run)
        return {
            "text": response_text,
            "tool_calls": tools_run,
            "source": "local-arsenal"
        }
