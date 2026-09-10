# 🤖 TONY AI — Unified Jarvis & Ultron Super-Assistant

**TONY** is an all-in-one AI desktop super-assistant combining the intelligence, loyalty, and wit of **JARVIS** with the tactical calculation, speed, and execution power of **ULTRON**.

---

## ⚡ Features

1. **Sci-Fi Arc Reactor Holographic HUD:**
   - Real-time HTML5 Canvas animation of a rotating, glowing Arc Reactor that reacts dynamically to states (`LISTENING`, `THINKING`, `SPEAKING`, `EXECUTING`).
   - Live hardware telemetry dials for CPU, RAM, battery/power, and OS status.
   - Built-in sound synthesis (Web Audio API) for futuristic HUD interactions.

2. **Multimodal Vision & Screen Awareness:**
   - Real-time desktop capture and visual reasoning ("What is on my screen?", "Summarize this page").

3. **Complete Tool Arsenal:**
   - **System Diagnostics:** CPU load, RAM allocation, battery status, disk usage.
   - **App Launcher:** Open Notepad, Calculator, VS Code, Browser, Spotify, Terminal, and more.
   - **Information Retrieval:** DuckDuckGo / Google search, Wikipedia deep lookup, live weather forecast.
   - **Windows System Controls:** Volume up/down/mute, terminal command runner.

4. **Persistent Memory System:**
   - SQLite-backed memory for storing user preferences, notes, tasks, and conversation logs across sessions.

5. **Flexible Operational Modes:**
   - **HUD Web Mode (`--hud`):** Full browser dashboard + voice + text prompt interface.
   - **CLI Console Mode (`--cli`):** Instant terminal-based conversation and tool runner.
   - **Continuous Voice Agent Mode (`--voice`):** Hands-free background listener with wake word detection (*"Tony"*, *"Jarvis"*, *"Ultron"*).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd "C:\Users\Ritu Chaudhary\.gemini\antigravity\scratch\tony-ai"
pip install -r requirements.txt
```

### 2. Configure API Key (Optional for Advanced LLM & Vision)
Copy `.env.example` to `.env` and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TONY_MODEL=gemini-2.5-flash
```
*(Note: Tony will function seamlessly even without an API key using his built-in offline Arsenal Protocol!)*

### 3. Launch Tony

#### Option A: Full Holographic HUD (Recommended)
```bash
python main.py
```
*Opens `http://127.0.0.1:8000` automatically in your browser.*

#### Option B: Terminal Interactive Mode
```bash
python main.py --cli
```

#### Option C: Hands-Free Voice Listener
```bash
python main.py --voice
```

---

## 🛠️ Project Structure

```text
tony-ai/
├── config.py              # Configuration & Environment loading
├── requirements.txt       # Dependencies
├── main.py                # Main multi-mode launcher
├── core/
│   ├── brain.py           # Central reasoning engine & Gemini LLM bridge
│   ├── memory.py          # SQLite persistent memory & task manager
│   ├── tools.py           # Tool arsenal (Diagnostics, Apps, Search, Volume, Weather)
│   ├── vision.py          # Screen capture & visual awareness
│   └── voice.py           # Speech recognition & Text-to-Speech engine
├── server/
│   └── app.py             # FastAPI & WebSocket backend
└── frontend/
    ├── index.html         # Cyberpunk Arc Reactor UI
    ├── style.css          # Sci-fi neon HUD styling
    └── app.js             # Canvas visualizer, sound effects & WS client
```
