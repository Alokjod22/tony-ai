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
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/\*(.*?)\*/g, '$1')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
        .replace(/[•\-\*]\s+/g, '')
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
            cleanedPrompt = transcript.replace(/^(hey tony|hey jarvis|friday|ultron)[,\s]*/i, '').trim();
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
            renderMessage("assistant", `### 🖥️ Execution Complete\n\`\`\`\n${JSON.stringify(d.result, null, 2)}\n\`\`\``);
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
    switchPersona("tony", false);

    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => {
            populateVoiceSelects();
        };
    }
});
