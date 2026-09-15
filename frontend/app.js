// ==========================================================================
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
        testQuote: "Good evening, sir. Tactical telemetry and subagent swarms are operational."
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
        testQuote: "Right away, Boss. Diagnostics and subagents running at full capacity."
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

    const cfg = PERSONA_CONFIGS[personaId];
    const welcomeAvatar = document.getElementById("welcomeAvatar");
    const welcomeSender = document.getElementById("welcomeSender");
    const ambientText = document.getElementById("ambientText");

    if (welcomeAvatar) welcomeAvatar.innerText = cfg.avatar;
    if (welcomeSender) welcomeSender.innerText = cfg.title;
    if (ambientText) ambientText.innerText = personaId === "jarvis" ? "HEY JARVIS" : (personaId === "friday" ? "HEY FRIDAY" : (personaId === "ultron" ? "ULTRON" : "HEY TONY"));

    if (triggerVoice && voiceOutputEnabled) {
        speakResponse(cfg.testQuote);
    }
}

// 2. Audio Waveform Spectrum Canvas Visualizer
let visualizerAnimationId = null;
function initAudioVisualizer() {
    const canvas = document.getElementById("audioVisualizer");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const numBars = 16;
    let phase = 0;

    function renderVisualizer() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const cfg = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
        const color = cfg.color || "#ffd700";

        phase += 0.08;
        const isLive = isCurrentlySpeaking || isRecording;
        const maxBarHeight = canvas.height - 4;
        const barWidth = Math.floor(canvas.width / numBars) - 2;

        for (let i = 0; i < numBars; i++) {
            let magnitude = 0.15;
            if (isLive) {
                magnitude = 0.3 + 0.65 * Math.abs(Math.sin(phase + i * 0.45) * Math.cos(phase * 0.8 + i * 0.2));
            } else {
                magnitude = 0.15 + 0.1 * Math.sin(phase * 0.5 + i * 0.3);
            }

            const barHeight = Math.max(3, magnitude * maxBarHeight);
            const x = i * (barWidth + 2) + 2;
            const y = (canvas.height - barHeight) / 2;

            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = isLive ? 8 : 2;
            ctx.fillRect(x, y, barWidth, barHeight);
        }

        visualizerAnimationId = requestAnimationFrame(renderVisualizer);
    }

    if (visualizerAnimationId) cancelAnimationFrame(visualizerAnimationId);
    renderVisualizer();
}

// 3. Speech Synthesis & Dynamic Voice Calibration
function resolveVoiceForPersona(personaId) {
    if (!('speechSynthesis' in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;

    if (customPersonaVoices[personaId]) {
        const custom = voices.find(v => (v.voiceURI === customPersonaVoices[personaId] || v.name === customPersonaVoices[personaId]));
        if (custom) return custom;
    }

    const cfg = PERSONA_CONFIGS[personaId] || PERSONA_CONFIGS.tony;
    for (const kw of cfg.preferredKeywords) {
        const match = voices.find(v => v.name.toLowerCase().includes(kw.toLowerCase()) || v.lang.toLowerCase().includes(kw.toLowerCase()));
        if (match) return match;
    }

    return voices[0];
}

function speakResponse(text) {
    if (!voiceOutputEnabled || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();
    isCurrentlySpeaking = false;
    updateInterruptBtn(false);

    const cleanText = text
        .replace(/```[\s\S]*?```/g, "Code block omitted from speech.")
        .replace(/###\s+/g, "")
        .replace(/\*\*/g, "")
        .replace(/[•✓⚙️🛡️⚡👁️🌐⚔️💻📱📊🧠]/g, "")
        .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    const cfg = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
    const voice = resolveVoiceForPersona(currentPersona);
    if (voice) utterance.voice = voice;

    utterance.pitch = cfg.basePitch;
    utterance.rate = whisperMode ? (cfg.baseRate * 0.85) : (cfg.baseRate * userSpeedMultiplier);
    if (whisperMode) utterance.volume = 0.45;

    utterance.onstart = () => {
        isCurrentlySpeaking = true;
        updateInterruptBtn(true);
        if (recognition && isRecording && !continuousMode) {
            try { recognition.stop(); } catch(e){}
        }
    };

    utterance.onend = () => {
        isCurrentlySpeaking = false;
        updateInterruptBtn(false);
        if (continuousMode && !isRecording) {
            startSpeechRecognition();
        }
    };

    utterance.onerror = () => {
        isCurrentlySpeaking = false;
        updateInterruptBtn(false);
    };

    window.speechSynthesis.speak(utterance);
}

function bargeInInterrupt() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    isCurrentlySpeaking = false;
    updateInterruptBtn(false);
}

function updateInterruptBtn(speaking) {
    const btn = document.getElementById("interruptBtn");
    if (btn) btn.style.display = speaking ? "flex" : "none";
}

// 4. Speech Recognition (Push-to-Talk & Hands-Free Ambient)
function initSpeechRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) return;

    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        isRecording = true;
        updateMicUi(true);
    };

    recognition.onresult = (event) => {
        if (!event.results || !event.results[0]) return;
        const transcript = event.results[0][0].transcript.trim();
        if (!transcript) return;

        // Wake word trigger
        const lower = transcript.toLowerCase();
        const isWake = lower.startsWith("hey tony") || lower.startsWith("hey jarvis") || lower.startsWith("hey friday") || lower.startsWith("friday") || lower.startsWith("ultron");
        let cleanPrompt = transcript;

        if (isWake) {
            cleanPrompt = transcript.replace(/^(hey tony|hey jarvis|hey friday|friday|ultron)[,\s]*/i, "");
            if (lower.startsWith("hey jarvis")) switchPersona("jarvis");
            else if (lower.startsWith("hey friday") || lower.startsWith("friday")) switchPersona("friday");
            else if (lower.startsWith("ultron")) switchPersona("ultron");
            else if (lower.startsWith("hey tony")) switchPersona("tony");
        }

        if (cleanPrompt.trim()) {
            const input = document.getElementById("chatInput");
            if (input) input.value = cleanPrompt;
            sendChatMessage();
        }
    };

    recognition.onerror = () => {
        isRecording = false;
        updateMicUi(false);
    };

    recognition.onend = () => {
        isRecording = false;
        updateMicUi(false);
        if (continuousMode && !isCurrentlySpeaking) {
            setTimeout(startSpeechRecognition, 300);
        }
    };
}

function toggleVoiceInput() {
    if (isRecording) {
        stopSpeechRecognition();
    } else {
        bargeInInterrupt();
        startSpeechRecognition();
    }
}

function startSpeechRecognition() {
    if (!recognition) initSpeechRecognition();
    if (recognition && !isRecording) {
        try { recognition.start(); } catch(e){}
    }
}

function stopSpeechRecognition() {
    if (recognition && isRecording) {
        try { recognition.stop(); } catch(e){}
    }
}

function updateMicUi(recording) {
    const btn = document.getElementById("micBtn");
    const waves = document.getElementById("micWaves");
    const icon = document.getElementById("micIcon");
    if (btn) btn.classList.toggle("recording", recording);
    if (waves) waves.style.display = recording ? "flex" : "none";
    if (icon) icon.innerText = recording ? "🔴" : "🎙️";
}

// 5. Header Control Handlers
function toggleContinuousMode() {
    continuousMode = !continuousMode;
    const label = document.getElementById("continuousLabel");
    const btn = document.getElementById("continuousBtn");
    if (label) label.innerText = `👂 CONVERSATION: ${continuousMode ? 'ON' : 'OFF'}`;
    if (btn) btn.classList.toggle("active", continuousMode);
    if (continuousMode) startSpeechRecognition();
    else stopSpeechRecognition();
}

function toggleWhisperMode() {
    whisperMode = !whisperMode;
    const label = document.getElementById("whisperLabel");
    const btn = document.getElementById("whisperBtn");
    if (label) label.innerText = `🤫 WHISPER: ${whisperMode ? 'ON' : 'OFF'}`;
    if (btn) btn.classList.toggle("active", whisperMode);
}

function setSpeechRate(val) {
    userSpeedMultiplier = parseFloat(val) || 1.2;
}

function setSecurityMode(level) {
    currentSecurityMode = level;
    fetch("/api/security/level", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level: level })
    }).catch(()=>{});
}

function setReasoningMode(mode) {
    currentReasoningMode = mode;
}

function toggleVoiceOutput() {
    voiceOutputEnabled = !voiceOutputEnabled;
    const icon = document.getElementById("voiceIcon");
    if (icon) icon.innerText = voiceOutputEnabled ? "🔊" : "🔇";
    if (!voiceOutputEnabled) bargeInInterrupt();
}

// 6. Central Chat Execution Stream
function handleChatKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendChatMessage();
    }
}

function autoResizeChatInput(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}

async function sendChatMessage() {
    const input = document.getElementById("chatInput");
    if (!input) return;
    const text = input.value.trim();
    if (!text || isAwaitingChatResponse) return;

    // Guard duplicate trigger within 800ms
    const now = Date.now();
    if (text === lastTransmittedText && (now - lastTransmittedTime) < 800) return;
    lastTransmittedText = text;
    lastTransmittedTime = now;

    input.value = "";
    input.style.height = "auto";

    renderMessage("user", text);
    bargeInInterrupt();

    isAwaitingChatResponse = true;
    const thinkingId = renderThinkingBubble();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt: text,
                persona: currentPersona,
                reasoning_mode: currentReasoningMode
            })
        });

        const data = await res.json();
        removeThinkingBubble(thinkingId);

        renderAssistantResponse(data);
        if (data.text) {
            speakResponse(data.text);
        }
    } catch (err) {
        removeThinkingBubble(thinkingId);
        renderMessage("assistant", `### ⚠️ Tactical Subsystem Alert\nFailed to reach neural endpoint: \`${err.message}\``);
    } finally {
        isAwaitingChatResponse = false;
    }
}

function renderMessage(role, text) {
    const stream = document.getElementById("chatMessages");
    if (!stream) return;

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}`;

    const timeStr = new Date().toLocaleTimeString();
    const config = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
    const avatar = role === "user" ? "👤" : config.avatar;
    const sender = role === "user" ? "OPERATOR" : config.title;

    const parsedHtml = (typeof marked !== "undefined") ? marked.parse(text) : `<p>${escapeHtml(text)}</p>`;

    msgDiv.innerHTML = `
        <div class="msg-header">
            <span class="sender-avatar">${avatar}</span>
            <span class="sender-name">${sender}</span>
            <span class="msg-time">${timeStr}</span>
        </div>
        <div class="msg-bubble">
            ${parsedHtml}
        </div>
    `;

    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
}

function renderThinkingBubble() {
    const stream = document.getElementById("chatMessages");
    if (!stream) return null;

    const id = "think-" + Date.now();
    const div = document.createElement("div");
    div.id = id;
    div.className = "message assistant thinking";
    div.innerHTML = `
        <div class="msg-header">
            <span class="sender-avatar">${PERSONA_CONFIGS[currentPersona].avatar}</span>
            <span class="sender-name">${PERSONA_CONFIGS[currentPersona].title}</span>
            <span class="msg-time">PROCESSING</span>
        </div>
        <div class="msg-bubble">
            <div class="hud-thinking-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    stream.appendChild(div);
    stream.scrollTop = stream.scrollHeight;
    return id;
}

function removeThinkingBubble(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
}

function renderAssistantResponse(data) {
    const stream = document.getElementById("chatMessages");
    if (!stream) return;

    const msgDiv = document.createElement("div");
    msgDiv.className = "message assistant";

    const timeStr = new Date().toLocaleTimeString();
    const config = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
    const text = data.text || "Command executed.";
    const parsedHtml = (typeof marked !== "undefined") ? marked.parse(text) : `<p>${escapeHtml(text)}</p>`;

    const emotion = data.emotion || "FOCUSED";
    const confidence = data.confidence || 99.8;
    const reflection = data.reflection || "Self-reflection: Telemetry confirmed nominal across all subsystems.";

    let cardExtra = "";

    // Security Approval Modal Intercept
    if (data.intent === "SECURITY_APPROVAL" && data.approval_required) {
        const app = data.approval_required;
        cardExtra += `
            <div class="inline-approval-card" id="card-${app.approval_id}">
                <div class="approval-header">⚠️ SECURITY APPROVAL REQUIRED (${app.risk_level})</div>
                <p>${escapeHtml(app.description)}</p>
                <div class="approval-actions">
                    <button class="approval-btn auth" onclick="resolveApproval('${app.approval_id}', true, '${escapeHtml(app.command || '')}')">✓ AUTHORIZE ACTION</button>
                    <button class="approval-btn deny" onclick="resolveApproval('${app.approval_id}', false)">✕ BLOCK & ABORT</button>
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
            renderMessage("assistant", `### 🖥️ Execution Complete\n\`\`\`\n${JSON.stringify(d.result, null, 2)}\n\`\`\``);
        }
    } catch(e) {
        console.log(e);
    }
}

// 7. Quick Action Palette Triggers (All Output Directly in Chat)
function triggerQuickAction(type) {
    const input = document.getElementById("chatInput");
    if (!input) return;

    if (type === "hf_image") input.value = "Generate image of a futuristic hyper-tactical AI operating center in dark cyber space, photorealistic 8k";
    else if (type === "spawn_swarm") input.value = "Spawn swarm to perform 360-degree system optimization, code evaluation, and threat scan";
    else if (type === "run_code") input.value = "Run python:\nimport math\nprint(f'Stark Core Quantum Pi: {math.pi:.10f}')\nprint(f'Squares: {[x**2 for x in range(8)]}')";
    else if (type === "root_device") input.value = "How do I safely root this Android device using Magisk and fastboot without bricking?";
    else if (type === "flash_firmware") input.value = "Generate a safe fastboot firmware flashing plan for boot and recovery partitions";
    else if (type === "device_deep") input.value = "Detect connected Android device specs, bootloader lock status, and root state";
    else if (type === "query_vault") input.value = "Search vault for key project specifications and notes";

    else if (type === "run_protocol") input.value = "Execute protocol: Morning Tactical Brief";
    else if (type === "protocol_dev") input.value = "Execute protocol: Developer Kickoff";
    else if (type === "what_remember") input.value = "What do you remember about me and my projects?";
    else if (type === "add_memory") { promptAddMemory(); return; }
    else if (type === "screen_scan") { captureAndSendScreen(); return; }
    else if (type === "adb_devices") input.value = "List all connected Android ADB devices";
    else if (type === "logcat_errors") input.value = "Analyze recent logcat crash errors";
    else if (type === "git_status") input.value = "Check git repository status and commits";
    else if (type === "deep_research") input.value = "Deep research on next-generation autonomous AI multi-agent swarms";
    else if (type === "system_diag") input.value = "Run hardware diagnostics and check slow PC";
    else if (type === "security_audit") input.value = "Run security sandbox audit";
    else if (type === "clear_chat") {
        const stream = document.getElementById("chatMessages");
        if (stream) stream.innerHTML = "";
        return;
    }

    sendChatMessage();
}

// 8. Vision & File / PDF Vault Ingestion
function captureAndSendScreen() {
    const input = document.getElementById("chatInput");
    if (input) input.value = "Inspect current screen and report all visible errors or UI elements.";
    sendChatMessage();
}

async function handleFileUpload(inputEl) {
    if (!inputEl.files || !inputEl.files[0]) return;
    const file = inputEl.files[0];
    
    renderMessage("user", `📎 Uploading to Knowledge Vault: **${file.name}** (${(file.size / 1024).toFixed(1)} KB)...`);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/api/vault/upload", {
            method: "POST",
            body: formData
        });
        const d = await res.json();
        if (d.success) {
            renderMessage("assistant", `### 📚 Knowledge Vault Ingestion Complete\n- **Document:** \`${d.filename}\`\n- **Indexed Chunks:** \`${d.chunks_count}\`\n- **Total Words:** \`${d.total_words}\`\n\n*Document indexed into permanent memory. You can now ask questions about this document in chat (e.g. 'Search vault for...').*`);
        } else {
            renderMessage("assistant", `### ⚠️ Vault Ingestion Notice\n${d.error || 'Failed to parse file contents.'}`);
        }
    } catch(err) {
        renderMessage("assistant", `### ⚠️ Upload Error\n${err.message}`);
    } finally {
        inputEl.value = "";
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
        renderMessage("assistant", `### 🧠 Memory Indexed Successfully\nTONY has permanently recorded: **"${escapeHtml(fact.trim())}"**.`);
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
    initAudioVisualizer();
    switchPersona("tony", false);

    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => {
            populateVoiceSelects();
        };
    }
});
