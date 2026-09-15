import asyncio
import json
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from pathlib import Path

from config import BASE_DIR, SERVER_HOST, SERVER_PORT
from core.memory import MemoryEngine
from core.security import SecurityCenter
from core.tools import ToolArsenal
from core.vision import VisionEngine
from core.workflows import WorkflowAndMissionEngine
from core.developer import DeveloperAndAndroidCore
from core.research import AutonomousResearchEngine
from core.sandbox import CodeSandboxEngine
from core.agents import AgentSwarmEngine
from core.vault import KnowledgeVaultEngine
from core.routines import ProtocolEngine
from core.huggingface_tools import HuggingFaceArsenal
from core.brain import TonyBrain
from core.voice import VoiceEngine

app = FastAPI(title="Tony AI Assistant // Super-Intelligence Matrix")

# Core Subsystems
memory = MemoryEngine()
security = SecurityCenter(memory=memory)
tools = ToolArsenal(memory_engine=memory, security_center=security)
vision = VisionEngine()
workflows = WorkflowAndMissionEngine(memory=memory, tools=tools)
developer = DeveloperAndAndroidCore(memory=memory)
research = AutonomousResearchEngine()
sandbox = CodeSandboxEngine()
swarm = AgentSwarmEngine()
vault = KnowledgeVaultEngine()
protocols = ProtocolEngine()
hf_tools = HuggingFaceArsenal()

brain = TonyBrain(
    memory=memory,
    tools=tools,
    vision=vision,
    security=security,
    workflows=workflows,
    developer=developer,
    research=research,
    sandbox=sandbox,
    swarm=swarm,
    vault=vault,
    protocols=protocols,
    hf_tools=hf_tools
)
voice = VoiceEngine()

# Mount Static Frontend
frontend_dir = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# --- Request Data Models ---
class ChatRequest(BaseModel):
    prompt: str
    persona: str = "tony"
    reasoning_mode: Optional[str] = "balanced"

class ActionApprovalRequest(BaseModel):
    approval_id: str
    approved: bool
    command: Optional[str] = None

class AddMemoryRequest(BaseModel):
    content: str
    category: str = "fact"
    importance: int = 3
    tags: Optional[List[str]] = None

class SetSecurityRequest(BaseModel):
    level: str

class ExecuteMissionRequest(BaseModel):
    mission_id: str

class RunWorkflowRequest(BaseModel):
    workflow_name: str

class CrashAnalysisRequest(BaseModel):
    log_text: str

class ResearchRequest(BaseModel):
    topic: str

class SandboxRunRequest(BaseModel):
    code: str
    auto_heal: Optional[bool] = True

class SwarmDispatchRequest(BaseModel):
    objective: str
    roles: Optional[List[str]] = None

class VaultQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4

class ExecuteProtocolRequest(BaseModel):
    protocol_id: str

class HFImageRequest(BaseModel):
    prompt: str

class HFSummarizeRequest(BaseModel):
    text: str

class HFSentimentRequest(BaseModel):
    text: str

# --- Static Routes ---
@app.get("/")
async def get_index():
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/style.css")
async def get_css():
    return FileResponse(str(frontend_dir / "style.css"))

@app.get("/app.js")
async def get_js():
    return FileResponse(str(frontend_dir / "app.js"))

# --- Core API Endpoints ---
@app.get("/api/telemetry")
async def get_telemetry():
    return tools.get_system_diagnostics()

@app.post("/api/chat")
async def handle_chat(req: ChatRequest):
    try:
        persona = (req.persona or "tony").lower()
        reasoning = req.reasoning_mode or "balanced"
        result = await brain.process_user_input(req.prompt, persona=persona, reasoning_mode=reasoning)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        fallback_res = brain._process_with_fallback_arsenal(req.prompt, persona=req.persona or "tony")
        return fallback_res

@app.post("/api/action/approve")
async def handle_action_approval(req: ActionApprovalRequest):
    if req.approved:
        if req.command:
            res = tools.run_terminal_command(req.command)
            return {"status": "executed", "result": res}
        return {"status": "authorized", "message": "Action execution confirmed by operator."}
    return {"status": "rejected", "message": "Action cancelled by operator."}

# --- 1. Memory Core Endpoints ---
@app.get("/api/memory")
async def get_all_memories():
    return memory.get_memories(limit=200)

@app.get("/api/memory/summary")
async def get_memory_summary():
    return memory.summarize_what_i_remember()

@app.post("/api/memory")
async def add_memory_entry(req: AddMemoryRequest):
    mid = memory.add_memory(content=req.content, category=req.category, importance=req.importance, tags=req.tags)
    return {"status": "success", "id": mid}

@app.delete("/api/memory/{memory_id}")
async def delete_memory_entry(memory_id: int):
    success = memory.delete_memory(memory_id)
    return {"status": "success" if success else "not_found"}

@app.get("/api/memory/export")
async def export_memory():
    json_str = memory.export_memory_data()
    return Response(content=json_str, media_type="application/json")

@app.post("/api/memory/import")
async def import_memory(req: Dict[str, Any]):
    return memory.import_memory_data(json.dumps(req))

# --- 2. Security & Sandbox Endpoints ---
@app.get("/api/security")
async def get_security_status():
    report = security.run_integrity_audit()
    report["audit_logs"] = memory.get_audit_logs(limit=20)
    return report

@app.post("/api/security/level")
async def update_security_level(req: SetSecurityRequest):
    return security.set_security_level(req.level)

# --- 3. Stark Sandbox & Live Interpreter Endpoints ---
@app.post("/api/sandbox/run")
async def run_sandbox_code(req: SandboxRunRequest):
    if req.auto_heal:
        return sandbox.self_heal_and_execute(req.code, brain_ref=brain)
    return sandbox.execute_python(req.code)

# --- 4. Subagent Swarm Endpoints ---
@app.post("/api/swarm/dispatch")
async def dispatch_swarm_endpoint(req: SwarmDispatchRequest):
    return swarm.dispatch_swarm(req.objective, agent_roles=req.roles)

# --- 5. Hugging Face Inference Multi-Modal Endpoints ---
@app.post("/api/hf/image")
async def hf_generate_image(req: HFImageRequest):
    return hf_tools.generate_image_hf(req.prompt)

@app.post("/api/hf/summarize")
async def hf_summarize_doc(req: HFSummarizeRequest):
    return hf_tools.summarize_text_hf(req.text)

@app.post("/api/hf/sentiment")
async def hf_analyze_sentiment(req: HFSentimentRequest):
    return hf_tools.classify_sentiment_hf(req.text)

# --- 6. Knowledge Vault & Document RAG Endpoints ---
@app.get("/api/vault/documents")
async def get_vault_docs():
    return vault.list_documents()

@app.post("/api/vault/query")
async def query_vault_endpoint(req: VaultQueryRequest):
    return vault.search_vault(req.query, top_k=req.top_k or 4)

@app.post("/api/vault/upload")
async def upload_vault_file(file: UploadFile = File(...)):
    try:
        content_bytes = await file.read()
        filename = file.filename
        
        upload_dir = BASE_DIR / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        dest_path = upload_dir / filename
        
        with open(dest_path, "wb") as f:
            f.write(content_bytes)
            
        extracted_text = vault.extract_text_from_file(str(dest_path))
        doc_type = filename.split(".")[-1].lower() if "." in filename else "text"
        
        res = vault.ingest_document(filename=filename, content=extracted_text, doc_type=doc_type)
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- 7. Protocols & Macro Engine Endpoints ---
@app.get("/api/protocols")
async def get_protocols_list():
    return protocols.list_protocols()

@app.post("/api/protocols/execute")
async def execute_protocol_endpoint(req: ExecuteProtocolRequest):
    return protocols.execute_protocol(req.protocol_id, brain_ref=brain)

# --- 8. Missions & Workflow Endpoints ---
@app.get("/api/missions")
async def get_missions_list():
    return workflows.get_available_missions()

@app.post("/api/missions/execute")
async def execute_mission_endpoint(req: ExecuteMissionRequest):
    return await workflows.execute_mission(req.mission_id)

@app.get("/api/workflows")
async def get_workflows():
    return workflows.custom_workflows

@app.post("/api/workflows/run")
async def run_workflow_endpoint(req: RunWorkflowRequest):
    return await workflows.run_workflow(req.workflow_name)

# --- 9. Developer & Android Endpoints ---
@app.get("/api/android/devices")
async def get_android_devices():
    return developer.list_adb_devices()

@app.get("/api/android/logcat")
async def get_android_logcat():
    return developer.get_logcat_errors()

@app.get("/api/developer/git")
async def get_git_status():
    return developer.git_status()

@app.post("/api/developer/crash")
async def analyze_crash(req: CrashAnalysisRequest):
    return developer.analyze_crash_log(req.log_text)

# --- 10. Autonomous Research Endpoints ---
@app.post("/api/research")
async def run_research(req: ResearchRequest):
    return research.perform_deep_research(req.topic)

# --- Real-Time WebSocket Channel ---
@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
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
                await asyncio.sleep(3.0)
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
            
            if data.get("type") == "chat":
                prompt = data.get("prompt", "")
                persona = (data.get("persona") or "tony").lower()
                res = await brain.process_user_input(prompt, persona=persona)
                await websocket.send_json({
                    "type": "chat_response",
                    "payload": res
                })
            elif data.get("type") == "mission_execute":
                mission_id = data.get("mission_id")
                async def progress_cb(state):
                    await websocket.send_json({
                        "type": "mission_update",
                        "payload": state
                    })
                await workflows.execute_mission(mission_id, callback=progress_cb)
    except WebSocketDisconnect:
        telemetry_task.cancel()
    except Exception:
        telemetry_task.cancel()
