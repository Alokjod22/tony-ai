import argparse
import sys
import webbrowser
import time
import asyncio
from config import SERVER_HOST, SERVER_PORT, WAKE_WORDS

def run_hud_mode():
    print("=====================================================")
    print("       TONY AI - SYSTEM ONLINE (HUD & VOICE MODE)     ")
    print("=====================================================")
    print(f"[*] Initializing Tony AI Core...")
    print(f"[*] Launching Holographic Web HUD on http://{SERVER_HOST}:{SERVER_PORT}")
    
    # Auto-open browser after a short delay
    def open_browser():
        time.sleep(1.2)
        webbrowser.open(f"http://{SERVER_HOST}:{SERVER_PORT}")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    from server.app import app
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)

def run_cli_mode():
    print("=====================================================")
    print("             TONY AI - CLI CONSOLE MODE              ")
    print("=====================================================")
    from core.memory import MemoryEngine
    from core.tools import ToolArsenal
    from core.vision import VisionEngine
    from core.brain import TonyBrain
    from core.voice import VoiceEngine

    memory = MemoryEngine()
    tools = ToolArsenal(memory_engine=memory)
    vision = VisionEngine()
    brain = TonyBrain(memory=memory, tools=tools, vision=vision)
    voice = VoiceEngine()

    voice.speak("Tony AI initialized in terminal mode. Standing by.")
    print("Type your command or prompt. Type 'exit' or 'quit' to terminate.\n")

    async def main_loop():
        while True:
            try:
                user_prompt = input("\nYou > ").strip()
                if not user_prompt:
                    continue
                if user_prompt.lower() in ["exit", "quit", "shutdown"]:
                    print("Tony > Powering down systems. Goodbye.")
                    voice.speak("Powering down systems. Goodbye.", block=True)
                    break

                res = await brain.process_user_input(user_prompt)
                print(f"\nTony > {res['text']}")
                if res.get("tool_calls"):
                    print(f"[Tools Executed]: {res['tool_calls']}")
                
                voice.speak(res["text"])
            except (KeyboardInterrupt, EOFError):
                break

    asyncio.run(main_loop())

def run_voice_loop():
    print("=====================================================")
    print("        TONY AI - CONTINUOUS VOICE AGENT MODE        ")
    print("=====================================================")
    from core.memory import MemoryEngine
    from core.tools import ToolArsenal
    from core.vision import VisionEngine
    from core.brain import TonyBrain
    from core.voice import VoiceEngine

    memory = MemoryEngine()
    tools = ToolArsenal(memory_engine=memory)
    vision = VisionEngine()
    brain = TonyBrain(memory=memory, tools=tools, vision=vision)
    voice = VoiceEngine()

    voice.speak("Tony AI listening. Say Tony, Jarvis, or Ultron to command.")
    print("[*] Listening for speech... (Say 'exit' to quit)\n")

    async def voice_worker():
        while True:
            phrase = voice.listen_once(timeout=6, phrase_time_limit=10)
            if phrase:
                print(f"[Heard]: {phrase}")
                lower = phrase.lower()
                if "exit" in lower or "shutdown" in lower:
                    voice.speak("Shutting down voice listener.", block=True)
                    break
                
                # Check for wake word or direct commands
                has_wake_word = any(w in lower for w in WAKE_WORDS)
                if has_wake_word or len(phrase.split()) > 2:
                    clean_query = phrase
                    for w in WAKE_WORDS:
                        clean_query = clean_query.lower().replace(w, "").strip()
                    if not clean_query:
                        clean_query = "Hello Tony"
                    
                    res = await brain.process_user_input(clean_query)
                    print(f"Tony > {res['text']}")
                    voice.speak(res["text"])

    asyncio.run(voice_worker())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tony AI Super-Assistant Launcher")
    parser.add_argument("--cli", action="store_true", help="Run Tony in terminal interactive mode")
    parser.add_argument("--voice", action="store_true", help="Run Tony in continuous microphone listening mode")
    parser.add_argument("--hud", action="store_true", help="Run Tony with Holographic Cyber HUD Web Interface (Default)")
    
    args = parser.parse_args()

    if args.cli:
        run_cli_mode()
    elif args.voice:
        run_voice_loop()
    else:
        run_hud_mode()
