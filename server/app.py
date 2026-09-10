import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from config import BASE_DIR, SERVER_HOST, SERVER_PORT
from core.memory import MemoryEngine
from core.tools import ToolArsenal
from core.vision import VisionEngine
from core.brain import TonyBrain
from core.voice import VoiceEngine

app = FastAPI(title="Tony AI Assistant")

# Core Subsystems
memory = MemoryEngine()
tools = ToolArsenal(memory_engine=memory)
vision = VisionEngine()
brain = TonyBrain(memory=memory, tools=tools, vision=vision)
voice = VoiceEngine()

# Mount Static Frontend
frontend_dir = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

class ChatRequest(BaseModel):
    prompt: str
    persona: Optional[str] = "tony"

@app.get("/")
async def get_index():
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/style.css")
async def get_css():
    return FileResponse(str(frontend_dir / "style.css"))

@app.get("/app.js")
async def get_js():
    return FileResponse(str(frontend_dir / "app.js"))

@app.get("/api/telemetry")
async def get_telemetry():
    return tools.get_system_diagnostics()

@app.post("/api/chat")
async def handle_chat(req: ChatRequest):
    try:
        persona = (req.persona or "tony").lower()
        result = await brain.process_user_input(req.prompt, persona=persona)
        # Speak result asynchronously via voice engine if local audio is available
        if result.get("text"):
            try:
                voice.speak(result["text"])
            except Exception:
                pass
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        fallback_res = brain._process_with_fallback_arsenal(req.prompt, persona=req.persona or "tony")
        return fallback_res

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Send initial telemetry
    try:
        await websocket.send_json({
            "type": "telemetry",
            "payload": tools.get_system_diagnostics()
        })
    except Exception:
        pass

    async def telemetry_loop():
        """Periodic hardware telemetry stream."""
        while True:
            try:
                await asyncio.sleep(2.5)
                diag = tools.get_system_diagnostics()
                await websocket.send_json({
                    "type": "telemetry",
                    "payload": diag
                })
            except Exception:
                break

    telemetry_task = asyncio.create_task(telemetry_loop())

    try:
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            
            if data.get("type") == "prompt":
                prompt = data.get("text", "")
                persona = data.get("persona", "tony")
                await websocket.send_json({"type": "state_change", "state": "THINKING"})
                
                result = await brain.process_user_input(prompt, persona=persona)
                
                await websocket.send_json({
                    "type": "response",
                    "payload": result
                })
                
                # Speak output via voice engine
                if result.get("text"):
                    voice.speak(result["text"])
                    
    except WebSocketDisconnect:
        telemetry_task.cancel()
    except Exception as e:
        print(f"[WS Server Error]: {e}")
        telemetry_task.cancel()

def start_server():
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)

if __name__ == "__main__":
    start_server()
