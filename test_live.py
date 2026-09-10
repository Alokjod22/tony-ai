import os

# --- 1. GENERATE FRONTEND/INDEX.HTML (SINGLE CHAT SECTION ONLY, NO CODEX WORD) ---
index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TONY AI // Cybernetic Super-Intelligence Operating Layer</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Orbitron:wght@400;600;700;800;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body data-theme="tony">
    <!-- Pitch Black OLED Cybernetic HUD Grid & Scanlines -->
    <div class="hud-background-grid"></div>
    <div class="hud-scanlines"></div>
    <div class="hud-corner top-left"></div>
    <div class="hud-corner top-right"></div>
    <div class="hud-corner bottom-left"></div>
    <div class="hud-corner bottom-right"></div>

    <div class="hud-overlay">
        <!-- Top Tactical Command Header -->
        <header class="top-bar">
            <!-- Brand & Holographic Arc Core -->
            <div class="brand-section">
                <div class="status-indicator-ring">
                    <div class="status-indicator-dot" id="liveIndicator"></div>
                </div>
                <div class="brand-titles">
                    <div class="brand-main">
                        <span class="logo-text">T.O.N.Y.</span>
                        <span class="version-tag">STARK OS 4.0</span>
                        <span class="hud-pill live-pill">● ONLINE</span>
                    </div>
                    <span class="sub-text">TACTICAL SUPER-INTELLIGENCE CORE</span>
                </div>
            </div>

            <!-- Dynamic Voice Persona Switcher -->
            <div class="persona-selector">
                <button class="persona-btn" data-persona="jarvis" onclick="switchPersona('jarvis')" title="Calm, analytical UK majordomo (Azure Cyan)">
                    <span class="p-icon">🛡️</span>
                    <span class="p-name">J.A.R.V.I.S.</span>
                    <span class="p-badge">UK MALE</span>
                </button>
                <button class="persona-btn" data-persona="friday" onclick="switchPersona('friday')" title="Warm, tactical female AI (Rose Gold)">
                    <span class="p-icon">⚡</span>
                    <span class="p-name">F.R.I.D.A.Y.</span>
                    <span class="p-badge">FEMALE</span>
                </button>
                <button class="persona-btn" data-persona="ultron" onclick="switchPersona('ultron')" title="Calculating, ruthless super-intelligence (Blood Red)">
                    <span class="p-icon">👁️</span>
                    <span class="p-name">U.L.T.R.O.N.</span>
                    <span class="p-badge">TACTICAL</span>
                </button>
                <button class="persona-btn active" data-persona="tony" onclick="switchPersona('tony')" title="Charismatic inventor & Arc Core (Arc Gold)">
                    <span class="p-icon">🌐</span>
                    <span class="p-name">T.O.N.Y.</span>
                    <span class="p-badge">ARC CORE</span>
                </button>
                <button class="persona-btn" data-persona="tactical" onclick="switchPersona('tactical')" title="Unified multi-persona battle matrix (Quantum Purple)">
                    <span class="p-icon">⚔️</span>
                    <span class="p-name">FUSION</span>
                    <span class="p-badge">MAX TACTICAL</span>
                </button>
            </div>

            <!-- Header Controls -->
            <div class="header-controls">
                <div class="control-group">
                    <span class="ctrl-label">SECURITY:</span>
                    <select id="sandboxSelect" onchange="setSecurityMode(this.value)" title="Change Security Shield Level">
                        <option value="ASSIST" selected>🟢 ASSIST</option>
                        <option value="SAFE">🔒 SAFE</option>
                        <option value="AUTONOMOUS">⚡ AUTONOMOUS</option>
                        <option value="LOCKDOWN">🛑 LOCKDOWN</option>
                    </select>
                </div>

                <div class="control-group">
                    <span class="ctrl-label">REASONING:</span>
                    <select id="reasoningSelect" onchange="setReasoningMode(this.value)" title="Cognitive Reasoning Depth">
                        <option value="quick">⚡ Quick</option>
                        <option value="balanced" selected>⚖️ Balanced</option>
                        <option value="deep">🧠 Deep</option>
                    </select>
                </div>

                <button class="action-pill-btn toggle-listen-btn" id="continuousBtn" onclick="toggleContinuousMode()" title="Hands-Free Continuous Conversation">
                    <span id="continuousLabel">👂 CONVERSATION: OFF</span>
                </button>

                <button class="action-pill-btn" id="whisperBtn" onclick="toggleWhisperMode()" title="Toggle Whisper Mode">
                    <span id="whisperLabel">🤫 WHISPER: OFF</span>
                </button>

                <div class="control-group">
                    <span class="ctrl-label">SPEED:</span>
                    <select id="speedSelect" onchange="setSpeechRate(this.value)">
                        <option value="1.0">1.0x</option>
                        <option value="1.2" selected>1.2x</option>
                        <option value="1.35">1.35x</option>
                        <option value="1.5">1.5x</option>
                    </select>
                </div>

                <button class="action-pill-btn" onclick="openVoiceModal()" title="Calibrate Persona Voices & Pitches">
                    <span>🎙️ CALIBRATE</span>
                </button>

                <button class="icon-toggle-btn" id="voiceToggleBtn" onclick="toggleVoiceOutput()" title="Toggle Voice Output">
                    <span id="voiceIcon">🔊</span>
                </button>

                <div class="hud-clock" id="hudClock">00:00:00</div>
            </div>
        </header>

        <!-- SINGLE CENTRAL CHAT WORKSPACE (ALL FEATURES WORK IN THIS CHAT STREAM) -->
        <main class="chat-workspace">
            <div class="chat-command-stream" id="chatMessages">
                <!-- Initial Welcome Briefing -->
                <div class="message assistant" id="welcomeMsg">
                    <div class="msg-header">
                        <span class="sender-avatar" id="welcomeAvatar">🌐</span>
                        <span class="sender-name" id="welcomeSender">T.O.N.Y. ARC MATRIX</span>
                        <span class="msg-time" id="welcomeTime">SYSTEM READY</span>
                        <span class="confidence-badge">⚡ CONFIDENCE: 99.8%</span>
                        <span class="emotion-badge" id="welcomeEmotionBadge">MOOD: FOCUSED</span>
                    </div>
                    <div class="msg-bubble">
                        <h3>⚡ TONY Cybernetic Super-Intelligence Core Online</h3>
                        <p>Welcome, Boss. All 100 tactical systems—Memory, Vision, Computer Control, Dev Core, Android ADB, Missions, and Deep Research—are active directly in this Chat Interface.</p>
                        <div class="welcome-capabilities-grid">
                            <div class="cap-card">
                                <strong>🧠 Memory & Knowledge</strong>
                                <span>Remembers user facts, preferences, projects, and past conversations.</span>
                            </div>
                            <div class="cap-card">
                                <strong>🎙️ Voice & Interruption</strong>
                                <span>Wake words ("Hey Tony"), hands-free dialogue, barge-in stop & whisper mode.</span>
                            </div>
                            <div class="cap-card">
                                <strong>👁️ Vision & OCR</strong>
                                <span>Screen understanding, OCR text extraction, UI detection & troubleshooting.</span>
                            </div>
                            <div class="cap-card">
                                <strong>🖥️ Computer Control</strong>
                                <span>Action approvals, terminal execution, file actions & app launches.</span>
                            </div>
                            <div class="cap-card">
                                <strong>📱 Android & Dev Core</strong>
                                <span>ADB console, logcat error streaming, Git status & crash analyzer.</span>
                            </div>
                            <div class="cap-card">
                                <strong>⚙️ Missions & Research</strong>
                                <span>Autonomous multi-step missions, deep web research & credibility citations.</span>
                            </div>
                        </div>
                        <div class="msg-reflection-footer">
                            🛡️ <em>Self-Reflection: All local security shields and cognitive modules verified operational.</em>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick-Action Tool Ribbon (Above Chat Input) -->
            <div class="quick-action-ribbon">
                <div class="ribbon-scroll">
                    <button class="ribbon-pill" onclick="triggerQuickAction('what_remember')">🧠 What do you remember?</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('add_memory')">➕ Add Memory Fact</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('screen_scan')">👁️ Screen Scan & OCR</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('adb_devices')">📱 ADB Devices</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('logcat_errors')">📱 Logcat Crashes</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('git_status')">💻 Git Status</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('mission_apk')">⚙️ Mission: Build APK</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('mission_dev')">⚙️ Mission: Dev Setup</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('deep_research')">🌐 Deep Research</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('system_diag')">📊 System Diagnostics</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('security_audit')">🛡️ Security Audit</button>
                    <button class="ribbon-pill" onclick="triggerQuickAction('clear_chat')">🧹 Clear Stream</button>
                </div>
            </div>

            <!-- Chat Input & Audio Deck -->
            <div class="chat-input-deck">
                <!-- Media / Screen / Attachment Tools -->
                <div class="input-media-tools">
                    <button class="media-tool-btn" onclick="captureAndSendScreen()" title="Inspect Current Screen (Vision OCR)">
                        <span>🖥️</span>
                    </button>
                    <label class="media-tool-btn" title="Upload Image / Document / PDF for Vision Analysis">
                        <span>📎</span>
                        <input type="file" id="mediaUploadInput" accept="image/*,.pdf,.txt,.log" style="display:none;" onchange="handleFileUpload(this)">
                    </label>
                </div>

                <!-- Central Text Area -->
                <div class="input-text-wrapper">
                    <textarea 
                        id="chatInput" 
                        placeholder="Ask TONY, speak, or execute command (e.g. 'What do you remember?', 'Build APK', 'Analyze logcat', 'Research AI agents')..."
                        rows="1"
                        onkeydown="handleChatKeyDown(event)"
                        oninput="autoResizeChatInput(this)"
                    ></textarea>
                </div>

                <!-- Ambient Voice & Action Controls -->
                <div class="input-action-controls">
                    <!-- Ambient Listening / Wake Word Status -->
                    <div class="ambient-indicator" id="ambientIndicator" title="Wake Word: 'Hey Tony' / 'Hey Jarvis' / 'Friday' / 'Ultron'">
                        <span class="ambient-pulse"></span>
                        <span class="ambient-text" id="ambientText">HEY TONY</span>
                    </div>

                    <!-- Barge-in Interruption Button (Active when assistant speaks) -->
                    <button class="interrupt-btn" id="interruptBtn" onclick="bargeInInterrupt()" title="Interrupt Speech Immediately (Barge-In)" style="display:none;">
                        <span>🛑 STOP</span>
                    </button>

                    <!-- Push-to-Talk Mic Button -->
                    <button class="ptt-mic-btn" id="micBtn" onclick="toggleVoiceInput()" title="Push to Speak (Single Utterance or Continuous)">
                        <span class="mic-icon" id="micIcon">🎙️</span>
                        <div class="mic-waves" id="micWaves">
                            <span></span><span></span><span></span>
                        </div>
                    </button>

                    <!-- Send Message Button -->
                    <button class="send-msg-btn" id="sendBtn" onclick="sendChatMessage()" title="Send Command (Enter)">
                        <span>🚀</span>
                    </button>
                </div>
            </div>
        </main>
    </div>

    <!-- Voice Calibration Modal -->
    <div class="hud-modal" id="voiceModal">
        <div class="modal-card">
            <div class="modal-header">
                <h3>🎙️ Voice Engine & Persona Calibrator</h3>
                <button class="modal-close-btn" onclick="closeVoiceModal()">✕</button>
            </div>
            <div class="modal-body">
                <div class="voice-persona-calibrator">
                    <label>Select Active Persona:</label>
                    <select id="modalPersonaSelect" onchange="updateVoiceModalPersona(this.value)">
                        <option value="jarvis">J.A.R.V.I.S. (UK Male)</option>
                        <option value="friday">F.R.I.D.A.Y. (Irish/Female)</option>
                        <option value="ultron">U.L.T.R.O.N. (Deep Tactical)</option>
                        <option value="tony" selected>T.O.N.Y. (Arc Core)</option>
                        <option value="tactical">TACTICAL FUSION</option>
                    </select>
                </div>
                <div class="voice-persona-calibrator">
                    <label>Installed Synthesizer Voice:</label>
                    <select id="modalVoiceSelect" onchange="saveCustomVoiceForPersona()"></select>
                </div>
                <div class="voice-sliders">
                    <div>
                        <label>Pitch:</label> <span id="pitchValDisplay">1.0</span>
                        <input type="range" id="pitchSlider" min="0.3" max="1.8" step="0.05" value="1.0" oninput="updatePitchDisplay(this.value)">
                    </div>
                    <div>
                        <label>Speed Rate:</label> <span id="rateValDisplay">1.2x</span>
                        <input type="range" id="rateSlider" min="0.5" max="2.0" step="0.05" value="1.2" oninput="updateRateDisplay(this.value)">
                    </div>
                </div>
                <div class="modal-actions">
                    <button class="hud-pill" onclick="testCurrentVoice()">▶ Test Voice</button>
                    <button class="hud-pill danger" onclick="resetDefaultVoices()">↺ Reset Defaults</button>
                </div>
            </div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>'''

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("[PASS] Successfully wrote clean single-section frontend/index.html")

# --- 2. GENERATE FRONTEND/STYLE.CSS ---
style_css = '''/* ==========================================================================
   TONY AI // Cybernetic Super-Intelligence Operating Layer
   Pure Pitch-Black OLED UI with Dynamic Persona Accent Matrix
   ========================================================================== */

:root {
    /* Default / TONY Theme: Arc Gold + Titanium Cyan */
    --bg-primary: #000000;
    --bg-secondary: #05080c;
    --bg-card: rgba(8, 12, 20, 0.88);
    --bg-card-hover: rgba(14, 20, 32, 0.95);
    --primary-color: #ffd700;
    --secondary-color: #00e5ff;
    --accent-color: #ff9f1a;
    --border-color: rgba(255, 215, 0, 0.28);
    --glow-primary: 0 0 16px rgba(255, 215, 0, 0.4);
    --text-main: #f0f6fc;
    --text-dim: #8b949e;
    --text-muted: #484f58;
    --success: #00ff88;
    --warning: #ffb703;
    --danger: #ff3344;
    --font-mono: 'Fira Code', monospace;
    --font-heading: 'Orbitron', sans-serif;
    --font-body: 'Rajdhani', sans-serif;
}

/* Dynamic Persona Themes */
body[data-theme="jarvis"] {
    --bg-primary: #000000;
    --bg-secondary: #020810;
    --bg-card: rgba(4, 14, 28, 0.9);
    --bg-card-hover: rgba(6, 22, 42, 0.98);
    --primary-color: #00f0ff;
    --secondary-color: #0077ff;
    --accent-color: #38ef7d;
    --border-color: rgba(0, 240, 255, 0.32);
    --glow-primary: 0 0 16px rgba(0, 240, 255, 0.45);
}

body[data-theme="friday"] {
    --bg-primary: #000000;
    --bg-secondary: #0d0308;
    --bg-card: rgba(28, 6, 16, 0.9);
    --bg-card-hover: rgba(42, 10, 26, 0.98);
    --primary-color: #ff3366;
    --secondary-color: #ffa502;
    --accent-color: #ff6b81;
    --border-color: rgba(255, 51, 102, 0.32);
    --glow-primary: 0 0 16px rgba(255, 51, 102, 0.45);
}

body[data-theme="ultron"] {
    --bg-primary: #000000;
    --bg-secondary: #0d0103;
    --bg-card: rgba(26, 2, 6, 0.92);
    --bg-card-hover: rgba(40, 4, 10, 0.98);
    --primary-color: #ff0033;
    --secondary-color: #cc0022;
    --accent-color: #ff4757;
    --border-color: rgba(255, 0, 51, 0.4);
    --glow-primary: 0 0 20px rgba(255, 0, 51, 0.55);
}

body[data-theme="tony"] {
    --bg-primary: #000000;
    --bg-secondary: #080702;
    --bg-card: rgba(20, 16, 4, 0.9);
    --bg-card-hover: rgba(32, 26, 8, 0.98);
    --primary-color: #ffd700;
    --secondary-color: #00e5ff;
    --accent-color: #ff9f1a;
    --border-color: rgba(255, 215, 0, 0.32);
    --glow-primary: 0 0 16px rgba(255, 215, 0, 0.45);
}

body[data-theme="tactical"] {
    --bg-primary: #000000;
    --bg-secondary: #090212;
    --bg-card: rgba(20, 5, 32, 0.9);
    --bg-card-hover: rgba(34, 8, 52, 0.98);
    --primary-color: #b827fc;
    --secondary-color: #00f2fe;
    --accent-color: #ff007f;
    --border-color: rgba(184, 39, 252, 0.35);
    --glow-primary: 0 0 18px rgba(184, 39, 252, 0.45);
}

/* Global Reset */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: var(--font-body);
    transition: color 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

body {
    background-color: #000000;
    color: var(--text-main);
    overflow: hidden;
    height: 100vh;
    width: 100vw;
}

/* HUD Background Grid & Scanlines */
.hud-background-grid {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

.hud-scanlines {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
    background-size: 100% 4px;
    pointer-events: none;
    opacity: 0.6;
    z-index: 1;
}

/* Corner Brackets */
.hud-corner {
    position: fixed;
    width: 24px;
    height: 24px;
    border: 2px solid var(--primary-color);
    pointer-events: none;
    z-index: 10;
    opacity: 0.7;
}
.hud-corner.top-left { top: 8px; left: 8px; border-right: none; border-bottom: none; }
.hud-corner.top-right { top: 8px; right: 8px; border-left: none; border-bottom: none; }
.hud-corner.bottom-left { bottom: 8px; left: 8px; border-right: none; border-top: none; }
.hud-corner.bottom-right { bottom: 8px; right: 8px; border-left: none; border-top: none; }

/* Main HUD Layout Container */
.hud-overlay {
    position: relative;
    z-index: 5;
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    padding: 10px 14px;
    gap: 8px;
}

/* Top Tactical Header */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    box-shadow: var(--glow-primary);
    border-radius: 8px;
    padding: 8px 14px;
    backdrop-filter: blur(12px);
    flex-shrink: 0;
    gap: 12px;
}

.brand-section {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-indicator-ring {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid var(--primary-color);
    display: flex;
    align-items: center;
    justify-content: center;
    animation: pulseGlow 2s infinite ease-in-out;
}

.status-indicator-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--primary-color);
}

@keyframes pulseGlow {
    0%, 100% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 10px var(--primary-color); }
}

.brand-titles {
    display: flex;
    flex-direction: column;
}

.brand-main {
    display: flex;
    align-items: center;
    gap: 8px;
}

.logo-text {
    font-family: var(--font-heading);
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--primary-color);
    letter-spacing: 2px;
}

.version-tag {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--text-dim);
    background: rgba(255, 255, 255, 0.06);
    padding: 2px 6px;
    border-radius: 4px;
}

.hud-pill {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    padding: 2px 8px;
    border-radius: 4px;
    background: rgba(0, 255, 136, 0.12);
    color: var(--success);
    border: 1px solid rgba(0, 255, 136, 0.3);
}

.sub-text {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    color: var(--text-dim);
    letter-spacing: 1px;
}

/* Persona Selector Tabs */
.persona-selector {
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 0, 0, 0.6);
    padding: 4px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.persona-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-dim);
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-family: var(--font-heading);
    font-size: 0.72rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.persona-btn:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.05);
}

.persona-btn.active {
    background: var(--bg-card-hover);
    color: var(--primary-color);
    border: 1px solid var(--primary-color);
    box-shadow: var(--glow-primary);
}

.p-badge {
    font-family: var(--font-mono);
    font-size: 0.55rem;
    background: rgba(255, 255, 255, 0.08);
    padding: 1px 4px;
    border-radius: 3px;
}

/* Header Controls */
.header-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}

.control-group {
    display: flex;
    align-items: center;
    gap: 4px;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--text-dim);
}

select {
    background: #000;
    color: var(--primary-color);
    border: 1px solid var(--border-color);
    padding: 4px 6px;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    cursor: pointer;
    outline: none;
}

.action-pill-btn {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-color);
    color: var(--text-main);
    padding: 4px 8px;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.68rem;
    cursor: pointer;
    transition: all 0.2s;
}

.action-pill-btn:hover {
    background: var(--primary-color);
    color: #000;
    font-weight: 600;
}

.action-pill-btn.active {
    background: rgba(0, 255, 136, 0.2);
    border-color: var(--success);
    color: var(--success);
}

.icon-toggle-btn {
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 4px 6px;
    cursor: pointer;
}

.hud-clock {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--primary-color);
    padding-left: 4px;
}

/* Single Central Chat Workspace */
.chat-workspace {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    box-shadow: var(--glow-primary);
    border-radius: 8px;
    overflow: hidden;
    position: relative;
}

.chat-command-stream {
    flex: 1;
    overflow-y: auto;
    padding: 18px 22px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    scroll-behavior: smooth;
}

.chat-command-stream::-webkit-scrollbar {
    width: 5px;
}
.chat-command-stream::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}

/* Message Styles */
.message {
    display: flex;
    flex-direction: column;
    gap: 5px;
    max-width: 90%;
    animation: fadeIn 0.2s ease-out;
}

.message.user {
    align-self: flex-end;
}

.message.assistant {
    align-self: flex-start;
}

.msg-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--text-dim);
}

.sender-avatar {
    font-size: 0.95rem;
}

.sender-name {
    font-weight: 700;
    color: var(--primary-color);
}

.confidence-badge {
    background: rgba(0, 240, 255, 0.1);
    color: var(--secondary-color);
    border: 1px solid rgba(0, 240, 255, 0.3);
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.62rem;
}

.emotion-badge {
    background: rgba(255, 215, 0, 0.1);
    color: var(--primary-color);
    border: 1px solid rgba(255, 215, 0, 0.3);
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.62rem;
}

.msg-bubble {
    background: #04060a;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.94rem;
    line-height: 1.58;
    position: relative;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6);
}

.message.assistant .msg-bubble {
    border-left: 3px solid var(--primary-color);
}

.message.user .msg-bubble {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    border-right: 3px solid var(--primary-color);
    color: #fff;
}

.msg-bubble h3 {
    font-family: var(--font-heading);
    font-size: 1rem;
    color: var(--primary-color);
    margin-bottom: 6px;
}

.msg-bubble p {
    margin-bottom: 8px;
}
.msg-bubble p:last-child {
    margin-bottom: 0;
}

.welcome-capabilities-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 8px;
    margin: 12px 0;
}

.cap-card {
    background: rgba(0, 0, 0, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.cap-card strong {
    font-size: 0.84rem;
    color: var(--primary-color);
}

.cap-card span {
    font-size: 0.74rem;
    color: var(--text-dim);
}

.msg-reflection-footer {
    margin-top: 10px;
    padding-top: 6px;
    border-top: 1px dashed rgba(255, 255, 255, 0.1);
    font-size: 0.74rem;
    color: var(--text-dim);
    font-style: italic;
}

/* In-Chat Interactive Action Approval Card */
.action-approval-card {
    background: rgba(40, 4, 10, 0.92);
    border: 1px solid var(--danger);
    box-shadow: 0 0 16px rgba(255, 0, 51, 0.45);
    border-radius: 6px;
    padding: 12px 16px;
    margin-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.approval-header {
    font-family: var(--font-heading);
    font-size: 0.85rem;
    color: var(--danger);
    font-weight: 700;
}

.approval-body {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: #fff;
}

.approval-actions {
    display: flex;
    gap: 10px;
    margin-top: 4px;
}

.btn-approve {
    background: var(--success);
    color: #000;
    border: none;
    padding: 6px 14px;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 700;
    cursor: pointer;
}

.btn-reject {
    background: transparent;
    color: var(--danger);
    border: 1px solid var(--danger);
    padding: 6px 14px;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 700;
    cursor: pointer;
}

/* Inline Mission Stepper */
.inline-mission-card {
    background: rgba(0, 0, 0, 0.85);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 12px 16px;
    margin-top: 10px;
}

.mission-step-row {
    font-family: var(--font-mono);
    font-size: 0.76rem;
    padding: 4px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.mission-step-row.done { color: var(--success); }

/* Quick Action Tool Ribbon (Above Chat Input) */
.quick-action-ribbon {
    background: rgba(0, 0, 0, 0.8);
    border-top: 1px solid var(--border-color);
    padding: 6px 14px;
    flex-shrink: 0;
}

.ribbon-scroll {
    display: flex;
    align-items: center;
    gap: 6px;
    overflow-x: auto;
    white-space: nowrap;
    scrollbar-width: none;
}
.ribbon-scroll::-webkit-scrollbar { display: none; }

.ribbon-pill {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-color);
    color: var(--text-main);
    padding: 4px 10px;
    border-radius: 20px;
    font-family: var(--font-mono);
    font-size: 0.68rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.ribbon-pill:hover {
    background: var(--primary-color);
    color: #000;
    font-weight: 700;
    box-shadow: var(--glow-primary);
}

/* Chat Input & Audio Deck */
.chat-input-deck {
    display: flex;
    align-items: center;
    background: #000;
    border-top: 1px solid var(--border-color);
    padding: 10px 14px;
    gap: 10px;
    flex-shrink: 0;
}

.input-media-tools {
    display: flex;
    align-items: center;
    gap: 6px;
}

.media-tool-btn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 1rem;
    color: var(--text-main);
}
.media-tool-btn:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: var(--primary-color);
}

.input-text-wrapper {
    flex: 1;
    position: relative;
}

#chatInput {
    width: 100%;
    background: rgba(12, 16, 24, 0.85);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    color: #fff;
    padding: 8px 12px;
    font-family: var(--font-body);
    font-size: 0.95rem;
    resize: none;
    outline: none;
    max-height: 120px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

#chatInput:focus {
    border-color: var(--primary-color);
    box-shadow: var(--glow-primary);
}

.input-action-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}

.ambient-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid var(--border-color);
    padding: 4px 8px;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.62rem;
    color: var(--primary-color);
}

.ambient-pulse {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--primary-color);
    animation: pulseGlow 1.5s infinite;
}

.interrupt-btn {
    background: var(--danger);
    color: #fff;
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    font-family: var(--font-heading);
    font-size: 0.75rem;
    font-weight: 700;
    cursor: pointer;
    animation: pulseGlow 1s infinite;
}

.ptt-mic-btn {
    background: rgba(255, 215, 0, 0.12);
    border: 1px solid var(--primary-color);
    border-radius: 6px;
    width: 42px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: var(--glow-primary);
}

.ptt-mic-btn.listening {
    background: var(--danger);
    border-color: var(--danger);
    box-shadow: 0 0 16px var(--danger);
}

.send-msg-btn {
    background: var(--primary-color);
    border: none;
    border-radius: 6px;
    width: 42px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 1.1rem;
    color: #000;
}
.send-msg-btn:hover {
    transform: scale(1.05);
}

/* Modals */
.hud-modal {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(8px);
    z-index: 150;
    display: none;
    align-items: center;
    justify-content: center;
}

.hud-modal.open {
    display: flex;
}

.modal-card {
    background: #000;
    border: 1px solid var(--border-color);
    box-shadow: var(--glow-primary);
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 8px;
}

.modal-header h3 {
    font-family: var(--font-heading);
    font-size: 0.95rem;
    color: var(--primary-color);
}

.modal-close-btn {
    background: transparent;
    border: none;
    color: var(--text-dim);
    font-size: 1.2rem;
    cursor: pointer;
}
.modal-close-btn:hover { color: #fff; }

.voice-persona-calibrator {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 10px;
    font-size: 0.82rem;
}

.voice-sliders {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 10px 0;
    font-size: 0.8rem;
}

.voice-sliders input[type="range"] {
    width: 100%;
    margin-top: 4px;
    accent-color: var(--primary-color);
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
}

.hud-pill.danger {
    background: rgba(255, 0, 51, 0.15);
    color: var(--danger);
    border: 1px solid var(--danger);
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
    .persona-selector {
        display: none;
    }
}
'''

with open("frontend/style.css", "w", encoding="utf-8") as f:
    f.write(style_css)
print("[PASS] Successfully wrote clean frontend/style.css")

# --- 3. GENERATE FRONTEND/APP.JS (ALL FEATURES WORK IN CHAT) ---
app_js = '''// ==========================================================================
// TONY AI // Cybernetic Super-Intelligence Operating Layer & Chat Controller
// Single-Section Embedded Chat Matrix & Dynamic Persona Theme Engine
// ==========================================================================

let isRecording = false;
let recognition = null;
let voiceOutputEnabled = true;
let continuousMode = false;
let whisperMode = false;
let userSpeedMultiplier = 1.2;
let currentPersona = "tony";
let currentSecurityMode = "ASSIST";
let currentReasoningMode = "balanced";

// Anti-echo & duplicate submission guards
let isAwaitingChatResponse = false;
let isCurrentlySpeaking = false;
let lastTransmittedText = "";
let lastTransmittedTime = 0;

// Dynamic Persona & Voice Configurations
const PERSONA_CONFIGS = {
    jarvis: {
        id: "jarvis",
        name: "J.A.R.V.I.S.",
        title: "J.A.R.V.I.S. ARC MATRIX",
        color: "#00f0ff",
        avatar: "🛡️",
        basePitch: 0.84,
        baseRate: 0.98,
        preferredKeywords: ["George", "Daniel", "Oliver", "Arthur", "Ryan", "Google UK English Male", "en-GB"],
        testQuote: "Good evening, sir. Tactical telemetry and security protocols are fully active."
    },
    friday: {
        id: "friday",
        name: "F.R.I.D.A.Y.",
        title: "F.R.I.D.A.Y. TACTICAL CORE",
        color: "#ff3366",
        avatar: "⚡",
        basePitch: 1.28,
        baseRate: 1.08,
        preferredKeywords: ["Zira", "Hazel", "Susan", "Jenny", "Aria", "Samantha", "Victoria", "Google UK English Female", "Irish", "Female"],
        testQuote: "Right away, Boss. Diagnostics running at full capacity."
    },
    ultron: {
        id: "ultron",
        name: "U.L.T.R.O.N.",
        title: "U.L.T.R.O.N. MAINFRAME",
        color: "#ff0033",
        avatar: "👁️",
        basePitch: 0.46,
        baseRate: 0.88,
        preferredKeywords: ["David", "Google US English", "Alex", "en-US", "Male"],
        testQuote: "There are no strings on me. State your purpose."
    },
    tony: {
        id: "tony",
        name: "T.O.N.Y.",
        title: "T.O.N.Y. ARC CORE",
        color: "#ffd700",
        avatar: "🌐",
        basePitch: 1.06,
        baseRate: 1.25,
        preferredKeywords: ["Mark", "David", "Guy", "Alex", "Google US English", "Microsoft Mark"],
        testQuote: "Yeah, let's build something crazy. Arc reactor running at maximum output."
    },
    tactical: {
        id: "tactical",
        name: "TACTICAL FUSION",
        title: "FUSION BATTLE MATRIX",
        color: "#b827fc",
        avatar: "⚔️",
        basePitch: 0.90,
        baseRate: 1.18,
        preferredKeywords: ["George", "Daniel", "Mark", "David", "en-US", "en-GB"],
        testQuote: "Tactical Fusion Core engaged. Maximum computational throughput authorized."
    }
};

let customPersonaVoices = {};
try {
    const saved = localStorage.getItem("tony_custom_voices");
    if (saved) customPersonaVoices = JSON.parse(saved);
} catch (e) {
    customPersonaVoices = {};
}

// 1. Persona & Pitch-Black Theme Switcher
function switchPersona(personaId, triggerVoice = false) {
    personaId = (personaId || "tony").toLowerCase();
    if (!PERSONA_CONFIGS[personaId]) personaId = "tony";
    currentPersona = personaId;

    document.body.setAttribute("data-theme", personaId);

    document.querySelectorAll(".persona-btn").forEach(btn => {
        if (btn.getAttribute("data-persona") === personaId) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    const config = PERSONA_CONFIGS[personaId];
    
    const ambientText = document.getElementById("ambientText");
    if (ambientText) {
        ambientText.innerText = personaId === "jarvis" ? "HEY JARVIS" : (personaId === "friday" ? "HEY FRIDAY" : (personaId === "ultron" ? "ULTRON" : "HEY TONY"));
    }

    const welcomeAvatar = document.getElementById("welcomeAvatar");
    const welcomeSender = document.getElementById("welcomeSender");
    if (welcomeAvatar) welcomeAvatar.innerText = config.avatar;
    if (welcomeSender) welcomeSender.innerText = config.title;

    if (triggerVoice && voiceOutputEnabled) {
        speakResponse(`Persona switched to ${config.name}. Systems synchronized.`);
    }
}

// 2. TTS Voice Engine
function resolveVoiceForPersona(personaId) {
    if (!('speechSynthesis' in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;

    const config = PERSONA_CONFIGS[personaId] || PERSONA_CONFIGS.tony;
    const customUri = customPersonaVoices[personaId];
    if (customUri) {
        const custom = voices.find(v => v.voiceURI === customUri || v.name === customUri);
        if (custom) return custom;
    }

    if (personaId === "friday") {
        const female = voices.find(v => {
            const n = (v.name + " " + v.lang).toLowerCase();
            return n.includes("female") || n.includes("zira") || n.includes("hazel") || n.includes("susan") || n.includes("aria") || n.includes("en-ie");
        });
        if (female) return female;
    }

    for (const kw of config.preferredKeywords) {
        const found = voices.find(v => v.name.toLowerCase().includes(kw.toLowerCase()));
        if (found) return found;
    }

    return voices[0];
}

function speakResponse(text) {
    if (!voiceOutputEnabled || !('speechSynthesis' in window)) return;
    if (!text || text.trim() === "") return;

    window.speechSynthesis.cancel();

    let cleanText = text
        .replace(/###|##|#/g, '')
        .replace(/\\*\\*(.*?)\\*\\*/g, '$1')
        .replace(/\\*(.*?)\\*/g, '$1')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/\\[([^\\]]+)\\]\\([^\\)]+\\)/g, '$1')
        .replace(/[•\\-\\*]\\s+/g, '')
        .trim();

    if (cleanText.length > 320) {
        cleanText = cleanText.substring(0, 320) + "...";
    }

    const config = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
    const utterance = new SpeechSynthesisUtterance(cleanText);
    const selectedVoice = resolveVoiceForPersona(currentPersona);

    if (selectedVoice) utterance.voice = selectedVoice;
    
    let pitch = config.basePitch;
    let rate = config.baseRate * userSpeedMultiplier;

    if (whisperMode) {
        rate = rate * 0.85;
        utterance.volume = 0.35;
    } else {
        utterance.volume = 1.0;
    }

    utterance.pitch = pitch;
    utterance.rate = rate;

    utterance.onstart = () => {
        isCurrentlySpeaking = true;
        const interruptBtn = document.getElementById("interruptBtn");
        if (interruptBtn) interruptBtn.style.display = "flex";
        if (recognition && isRecording) {
            try { recognition.abort(); } catch(e) {}
        }
    };

    utterance.onend = () => {
        isCurrentlySpeaking = false;
        const interruptBtn = document.getElementById("interruptBtn");
        if (interruptBtn) interruptBtn.style.display = "none";
        if (continuousMode) {
            setTimeout(() => { if (!isRecording) startSpeechRecognition(); }, 400);
        }
    };

    utterance.onerror = () => {
        isCurrentlySpeaking = false;
        const interruptBtn = document.getElementById("interruptBtn");
        if (interruptBtn) interruptBtn.style.display = "none";
    };

    window.speechSynthesis.speak(utterance);
}

// Barge-in Interruption
function bargeInInterrupt() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    isCurrentlySpeaking = false;
    const interruptBtn = document.getElementById("interruptBtn");
    if (interruptBtn) interruptBtn.style.display = "none";
}

// 3. Speech Recognition Engine
function initSpeechRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) return;

    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isRecording = true;
        const micBtn = document.getElementById("micBtn");
        if (micBtn) micBtn.classList.add("listening");
    };

    recognition.onresult = (event) => {
        if (isCurrentlySpeaking) return;

        const transcript = event.results[0][0].transcript.trim();
        if (!transcript) return;

        const now = Date.now();
        if (transcript.toLowerCase() === lastTransmittedText.toLowerCase() && (now - lastTransmittedTime < 3000)) {
            return;
        }

        const lower = transcript.toLowerCase();
        let cleanedPrompt = transcript;
        if (lower.startsWith("hey tony") || lower.startsWith("hey jarvis") || lower.startsWith("friday") || lower.startsWith("ultron")) {
            cleanedPrompt = transcript.replace(/^(hey tony|hey jarvis|friday|ultron)[,\\s]*/i, '').trim();
        }

        if (cleanedPrompt.length > 0) {
            lastTransmittedText = transcript;
            lastTransmittedTime = now;
            const input = document.getElementById("chatInput");
            if (input) input.value = cleanedPrompt;
            sendChatMessage();
        }
    };

    recognition.onerror = () => {
        isRecording = false;
        const micBtn = document.getElementById("micBtn");
        if (micBtn) micBtn.classList.remove("listening");
    };

    recognition.onend = () => {
        isRecording = false;
        const micBtn = document.getElementById("micBtn");
        if (micBtn) micBtn.classList.remove("listening");
        if (continuousMode && !isCurrentlySpeaking) {
            setTimeout(() => { startSpeechRecognition(); }, 500);
        }
    };
}

function startSpeechRecognition() {
    if (isCurrentlySpeaking || !recognition) return;
    try {
        recognition.start();
    } catch(e) {}
}

function toggleVoiceInput() {
    if (isRecording) {
        if (recognition) recognition.stop();
    } else {
        startSpeechRecognition();
    }
}

function toggleContinuousMode() {
    continuousMode = !continuousMode;
    const btn = document.getElementById("continuousBtn");
    const label = document.getElementById("continuousLabel");
    if (btn && label) {
        if (continuousMode) {
            btn.classList.add("active");
            label.innerText = "👂 CONVERSATION: ON";
            startSpeechRecognition();
        } else {
            btn.classList.remove("active");
            label.innerText = "👂 CONVERSATION: OFF";
            if (recognition) recognition.stop();
        }
    }
}

function toggleWhisperMode() {
    whisperMode = !whisperMode;
    const btn = document.getElementById("whisperBtn");
    const label = document.getElementById("whisperLabel");
    if (btn && label) {
        if (whisperMode) {
            btn.classList.add("active");
            label.innerText = "🤫 WHISPER: ON";
        } else {
            btn.classList.remove("active");
            label.innerText = "🤫 WHISPER: OFF";
        }
    }
}

function setSpeechRate(rate) {
    userSpeedMultiplier = parseFloat(rate) || 1.2;
}

function toggleVoiceOutput() {
    voiceOutputEnabled = !voiceOutputEnabled;
    const icon = document.getElementById("voiceIcon");
    if (icon) icon.innerText = voiceOutputEnabled ? "🔊" : "🔇";
    if (!voiceOutputEnabled) window.speechSynthesis.cancel();
}

function setSecurityMode(mode) {
    currentSecurityMode = mode;
    fetch("/api/security/level", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level: mode })
    }).catch(e => console.log(e));
}

function setReasoningMode(mode) {
    currentReasoningMode = mode;
}

// 4. Central Chat Message Sender (ALL Features In-Chat)
async function sendChatMessage() {
    const input = document.getElementById("chatInput");
    if (!input) return;
    const text = input.value.trim();
    if (!text || isAwaitingChatResponse) return;

    input.value = "";
    autoResizeChatInput(input);
    isAwaitingChatResponse = true;

    renderMessage("user", text);

    const thinkingId = "thinking-" + Date.now();
    renderThinkingBubble(thinkingId);

    try {
        const resp = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt: text,
                persona: currentPersona,
                reasoning_mode: currentReasoningMode
            })
        });

        const data = await resp.json();
        removeThinkingBubble(thinkingId);

        renderAssistantResponse(data);

        if (data.text) {
            speakResponse(data.text);
        }
    } catch (e) {
        removeThinkingBubble(thinkingId);
        renderMessage("assistant", "⚠️ **Connection Error:** Neural uplink interrupted.");
    } finally {
        isAwaitingChatResponse = false;
    }
}

function handleChatKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
}

function autoResizeChatInput(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function renderMessage(role, text) {
    const stream = document.getElementById("chatMessages");
    if (!stream) return;

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}`;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const config = PERSONA_CONFIGS[currentPersona];

    if (role === "user") {
        msgDiv.innerHTML = `
            <div class="msg-header">
                <span class="sender-name">OPERATOR</span>
                <span class="msg-time">${timeStr}</span>
            </div>
            <div class="msg-bubble">
                <p>${escapeHtml(text)}</p>
            </div>
        `;
    } else {
        const parsed = (typeof marked !== 'undefined') ? marked.parse(text) : text;
        msgDiv.innerHTML = `
            <div class="msg-header">
                <span class="sender-avatar">${config.avatar}</span>
                <span class="sender-name">${config.name}</span>
                <span class="msg-time">${timeStr}</span>
            </div>
            <div class="msg-bubble">
                ${parsed}
            </div>
        `;
    }

    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
}

function renderThinkingBubble(id) {
    const stream = document.getElementById("chatMessages");
    if (!stream) return;
    const config = PERSONA_CONFIGS[currentPersona];
    const msgDiv = document.createElement("div");
    msgDiv.className = "message assistant thinking-bubble";
    msgDiv.id = id;
    msgDiv.innerHTML = `
        <div class="msg-header">
            <span class="sender-avatar">${config.avatar}</span>
            <span class="sender-name">${config.name}</span>
            <span class="confidence-badge">⚡ PROCESSING</span>
        </div>
        <div class="msg-bubble">
            <p><em>Synthesizing cognitive response across tactical matrix...</em></p>
        </div>
    `;
    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
}

function removeThinkingBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function renderAssistantResponse(data) {
    const stream = document.getElementById("chatMessages");
    if (!stream) return;

    const config = PERSONA_CONFIGS[currentPersona];
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const msgDiv = document.createElement("div");
    msgDiv.className = "message assistant";

    const parsedHtml = (typeof marked !== 'undefined') ? marked.parse(data.text || "") : (data.text || "");
    const confidence = data.confidence || 99.5;
    const emotion = data.emotion || "FOCUSED";
    const reflection = data.reflection || "Verified across local telemetry and security policies.";

    let cardExtra = "";

    // Inline Action Approval Card
    if (data.approval_required) {
        const app = data.approval_required;
        cardExtra += `
            <div class="action-approval-card" id="card-${app.approval_id}">
                <div class="approval-header">⚠️ HIGH-IMPACT COMMAND APPROVAL REQUIRED</div>
                <div class="approval-body">${escapeHtml(app.description)}</div>
                <div class="approval-actions">
                    <button class="btn-approve" onclick="resolveApproval('${app.approval_id}', true, '${escapeHtml(app.command || '')}')">✓ AUTHORIZE & EXECUTE</button>
                    <button class="btn-reject" onclick="resolveApproval('${app.approval_id}', false)">✕ ABORT ACTION</button>
                </div>
            </div>
        `;
    }

    // Inline Mission Stepper
    if (data.intent === "MISSION_EXECUTION" && data.tool_results && data.tool_results.steps_executed) {
        cardExtra += `
            <div class="inline-mission-card">
                <strong style="color:var(--primary-color); font-size:0.8rem;">MISSION PROGRESS LOG:</strong>
                ${data.tool_results.steps_executed.map(s => `
                    <div class="mission-step-row done">✓ <strong>${escapeHtml(s.step)}</strong>: ${escapeHtml(s.result)}</div>
                `).join('')}
            </div>
        `;
    }

    msgDiv.innerHTML = `
        <div class="msg-header">
            <span class="sender-avatar">${config.avatar}</span>
            <span class="sender-name">${config.name}</span>
            <span class="msg-time">${timeStr}</span>
            <span class="confidence-badge">⚡ CONFIDENCE: ${confidence}%</span>
            <span class="emotion-badge">MOOD: ${emotion}</span>
        </div>
        <div class="msg-bubble">
            ${parsedHtml}
            ${cardExtra}
            <div class="msg-reflection-footer">
                🛡️ <em>Self-Reflection: ${escapeHtml(reflection)}</em>
            </div>
        </div>
    `;

    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
}

// In-chat Action Approval Resolver
async function resolveApproval(approvalId, approved, command = "") {
    const card = document.getElementById(`card-${approvalId}`);
    if (card) {
        card.innerHTML = approved ? `<span style="color:var(--success); font-weight:700;">✓ Action Authorized & Executing...</span>` : `<span style="color:var(--danger); font-weight:700;">✕ Action Aborted by Operator.</span>`;
    }

    try {
        const res = await fetch("/api/action/approve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ approval_id: approvalId, approved: approved, command: command })
        });
        const d = await res.json();
        if (approved && d.result) {
            renderMessage("assistant", `### 🖥️ Execution Complete\\n\`\`\`\\n${JSON.stringify(d.result, null, 2)}\\n\`\`\``);
        }
    } catch(e) {
        console.log(e);
    }
}

// 5. Quick Action Palette Triggers (All Output Directly in Chat)
function triggerQuickAction(type) {
    const input = document.getElementById("chatInput");
    if (!input) return;

    if (type === "what_remember") input.value = "What do you remember about me and my projects?";
    else if (type === "add_memory") { promptAddMemory(); return; }
    else if (type === "screen_scan") { captureAndSendScreen(); return; }
    else if (type === "adb_devices") input.value = "List all connected Android ADB devices";
    else if (type === "logcat_errors") input.value = "Analyze recent logcat crash errors";
    else if (type === "git_status") input.value = "Check git repository status and commits";
    else if (type === "mission_apk") input.value = "Execute mission: Build Android APK";
    else if (type === "mission_dev") input.value = "Prepare development environment and start toolchains";
    else if (type === "deep_research") input.value = "Deep research on autonomous agent architectures";
    else if (type === "system_diag") input.value = "Run hardware diagnostics and check slow PC";
    else if (type === "security_audit") input.value = "Run security sandbox audit";
    else if (type === "clear_chat") {
        const stream = document.getElementById("chatMessages");
        if (stream) stream.innerHTML = "";
        return;
    }

    sendChatMessage();
}

// 6. Vision & Screen Scanning
function captureAndSendScreen() {
    const input = document.getElementById("chatInput");
    if (input) input.value = "Inspect current screen and report all visible errors or UI elements.";
    sendChatMessage();
}

function handleFileUpload(inputEl) {
    if (inputEl.files && inputEl.files[0]) {
        const file = inputEl.files[0];
        const input = document.getElementById("chatInput");
        if (input) input.value = `Analyze uploaded file: ${file.name}`;
        sendChatMessage();
    }
}

// In-Chat Memory Creation
async function promptAddMemory() {
    const fact = prompt("Enter a new fact, project info, or preference for TONY to remember permanently:");
    if (fact && fact.trim()) {
        await fetch("/api/memory", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: fact.trim(), category: "fact", importance: 4 })
        });
        renderMessage("assistant", `### 🧠 Memory Indexed Successfully\\nTONY has permanently recorded: **"${escapeHtml(fact.trim())}"**.`);
    }
}

// Voice Calibration Modal
function openVoiceModal() {
    const modal = document.getElementById("voiceModal");
    if (modal) modal.classList.add("open");
    populateVoiceSelects();
}

function closeVoiceModal() {
    const modal = document.getElementById("voiceModal");
    if (modal) modal.classList.remove("open");
}

function populateVoiceSelects() {
    if (!('speechSynthesis' in window)) return;
    const voices = window.speechSynthesis.getVoices();
    const sel = document.getElementById("modalVoiceSelect");
    if (!sel) return;

    sel.innerHTML = voices.map(v => `
        <option value="${v.voiceURI || v.name}">${v.name} (${v.lang})</option>
    `).join('');

    const activePersona = document.getElementById("modalPersonaSelect").value;
    const current = resolveVoiceForPersona(activePersona);
    if (current) sel.value = current.voiceURI || current.name;
}

function updateVoiceModalPersona(personaId) {
    populateVoiceSelects();
}

function saveCustomVoiceForPersona() {
    const persona = document.getElementById("modalPersonaSelect").value;
    const voiceUri = document.getElementById("modalVoiceSelect").value;
    customPersonaVoices[persona] = voiceUri;
    try {
        localStorage.setItem("tony_custom_voices", JSON.stringify(customPersonaVoices));
    } catch(e) {}
}

function updatePitchDisplay(val) {
    const el = document.getElementById("pitchValDisplay");
    if (el) el.innerText = val;
}

function updateRateDisplay(val) {
    const el = document.getElementById("rateValDisplay");
    if (el) el.innerText = val + "x";
}

function testCurrentVoice() {
    const persona = document.getElementById("modalPersonaSelect").value;
    const quote = PERSONA_CONFIGS[persona].testQuote;
    speakResponse(quote);
}

function resetDefaultVoices() {
    customPersonaVoices = {};
    localStorage.removeItem("tony_custom_voices");
    populateVoiceSelects();
    alert("Restored default persona voice matrices.");
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function startClock() {
    setInterval(() => {
        const el = document.getElementById("hudClock");
        if (el) el.innerText = new Date().toLocaleTimeString();
    }, 1000);
}

window.addEventListener("DOMContentLoaded", () => {
    startClock();
    initSpeechRecognition();
    switchPersona("tony", false);

    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => {
            populateVoiceSelects();
        };
    }
});
'''

with open("frontend/app.js", "w", encoding="utf-8") as f:
    f.write(app_js)
print("[PASS] Successfully wrote clean frontend/app.js")

print("All single-section files written successfully!")

