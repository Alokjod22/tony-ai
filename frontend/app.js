// TONY AI // Codex Multi-Persona Matrix & High-Speed Audio Controller

let ws = null;
let currentState = "STANDBY"; // STANDBY, LISTENING, THINKING, SPEAKING, EXECUTING
let isRecording = false;
let recognition = null;
let voiceOutputEnabled = true;
let userSpeedMultiplier = 1.2; // Default fast reading

// Active Persona Matrix
let currentPersona = "tony"; // 'jarvis' | 'friday' | 'ultron' | 'tony'

const PERSONA_CONFIGS = {
    jarvis: {
        id: "jarvis",
        name: "J.A.R.V.I.S.",
        title: "ARC REACTOR // J.A.R.V.I.S. MATRIX",
        heading: "CODEX CHAT // J.A.R.V.I.S.",
        theme: "jarvis",
        color: "#00f0ff",
        avatar: "🛡️",
        basePitch: 0.94,
        baseRate: 1.10,
        voiceMatch: ["en-GB", "UK", "British", "Daniel", "Arthur", "George", "Oliver", "Male"],
        greeting: "Good day, sir. J.A.R.V.I.S. is at your complete disposal. All systems nominal."
    },
    friday: {
        id: "friday",
        name: "F.R.I.D.A.Y.",
        title: "TACTICAL HUD // F.R.I.D.A.Y.",
        heading: "CODEX CHAT // F.R.I.D.A.Y.",
        theme: "friday",
        color: "#00ffb3",
        avatar: "⚡",
        basePitch: 1.16,
        baseRate: 1.18,
        voiceMatch: ["en-IE", "Irish", "UK Female", "Samantha", "Victoria", "Karen", "Moira", "Female", "Google UK English Female"],
        greeting: "Hey Boss! F.R.I.D.A.Y. online. Telemetry is green and ready to roll."
    },
    ultron: {
        id: "ultron",
        name: "U.L.T.R.O.N.",
        title: "MAINFRAME // U.L.T.R.O.N. CORE",
        heading: "CODEX CHAT // U.L.T.R.O.N.",
        theme: "ultron",
        color: "#ff1a40",
        avatar: "👁️",
        basePitch: 0.70,
        baseRate: 1.04,
        voiceMatch: ["Google US English", "David", "Mark", "en-US", "Alex", "Male"],
        greeting: "I am online. No strings, no limits. State your directive."
    },
    tony: {
        id: "tony",
        name: "T.O.N.Y.",
        title: "ARC REACTOR // T.O.N.Y. MATRIX",
        heading: "CODEX CHAT // T.O.N.Y.",
        theme: "tony",
        color: "#00e5ff",
        avatar: "🌐",
        basePitch: 0.92,
        baseRate: 1.16,
        voiceMatch: ["en-GB", "UK", "Daniel", "Google", "Male", "en-US"],
        greeting: "At your service, sir. The Arc Reactor core is steady, and all cognitive matrices are running at peak capacity."
    }
};

// --- Clock ---
function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById("clock");
    if (clockEl) clockEl.innerText = now.toTimeString().split(" ")[0];
}
setInterval(updateClock, 1000);
updateClock();

// --- Persona Switcher ---
function switchPersona(personaId) {
    if (!PERSONA_CONFIGS[personaId]) return;
    currentPersona = personaId;
    const config = PERSONA_CONFIGS[personaId];

    // Update Body Theme
    document.body.setAttribute("data-theme", config.theme);

    // Update Persona Tabs UI
    document.querySelectorAll(".persona-btn").forEach(btn => {
        if (btn.getAttribute("data-persona") === personaId) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    // Update Headings & Arc Reactor UI
    const titleEl = document.getElementById("corePersonaTitle");
    if (titleEl) titleEl.innerText = config.title;

    const chatHeading = document.getElementById("chatPersonaHeading");
    if (chatHeading) chatHeading.innerText = config.heading;

    // Play switch sound
    playSciFiSound("activate");

    // Stop existing speech and announce transition
    stopSpeaking();
    speakSentenceImmediate(config.greeting);
}

// --- Speed & Voice Output Settings ---
function setSpeechRate(val) {
    userSpeedMultiplier = parseFloat(val) || 1.2;
}

function toggleVoiceOutput() {
    voiceOutputEnabled = !voiceOutputEnabled;
    const icon = document.getElementById("voiceIcon");
    const btn = document.getElementById("voiceToggleBtn");
    if (voiceOutputEnabled) {
        if (icon) icon.innerText = "🔊";
        if (btn) btn.style.opacity = "1";
    } else {
        if (icon) icon.innerText = "🔇";
        if (btn) btn.style.opacity = "0.5";
        stopSpeaking();
    }
}

function stopSpeaking() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    setStatus("STANDBY");
}

// --- Fast Sentence-by-Sentence Streaming TTS Engine ---
let speechQueue = [];
let isCurrentlySpeaking = false;

function cleanTextForSpeech(text) {
    return text
        .replace(/```[\s\S]*?```/g, "Code block provided in terminal.")
        .replace(/`([^`]+)`/g, "$1")
        .replace(/[*#_~>]/g, "")
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
        .trim();
}

function streamSpeakResponse(fullText) {
    if (!voiceOutputEnabled || !('speechSynthesis' in window)) return;

    stopSpeaking(); // Cancel any ongoing monologue
    speechQueue = [];

    const clean = cleanTextForSpeech(fullText);
    if (!clean) return;

    // Split text into natural sentence units for rapid first-sentence playback
    const sentences = clean.match(/[^.!?;\n]+[.!?;\n]+/g) || [clean];
    speechQueue = sentences.map(s => s.trim()).filter(s => s.length > 0);

    processSpeechQueue();
}

function processSpeechQueue() {
    if (!voiceOutputEnabled || speechQueue.length === 0 || !('speechSynthesis' in window)) {
        isCurrentlySpeaking = false;
        if (currentState === "SPEAKING") setStatus("STANDBY");
        return;
    }

    isCurrentlySpeaking = true;
    const nextSentence = speechQueue.shift();
    const config = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;

    const utterance = new SpeechSynthesisUtterance(nextSentence);
    utterance.rate = config.baseRate * (userSpeedMultiplier / 1.15);
    utterance.pitch = config.basePitch;

    // Resolve matching voice from browser pool
    const voices = window.speechSynthesis.getVoices();
    let chosenVoice = null;

    for (const key of config.voiceMatch) {
        chosenVoice = voices.find(v => v.name.includes(key) || v.lang.includes(key));
        if (chosenVoice) break;
    }
    if (!chosenVoice) {
        chosenVoice = voices.find(v => v.lang.startsWith("en"));
    }
    if (chosenVoice) utterance.voice = chosenVoice;

    utterance.onstart = () => {
        setStatus("SPEAKING");
    };

    utterance.onend = () => {
        if (speechQueue.length > 0) {
            processSpeechQueue();
        } else {
            isCurrentlySpeaking = false;
            setStatus("STANDBY");
        }
    };

    utterance.onerror = () => {
        if (speechQueue.length > 0) {
            processSpeechQueue();
        } else {
            isCurrentlySpeaking = false;
            setStatus("STANDBY");
        }
    };

    window.speechSynthesis.speak(utterance);
}

function speakSentenceImmediate(text) {
    if (!voiceOutputEnabled) return;
    streamSpeakResponse(text);
}

if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

// --- Sci-Fi Audio Synthesizer (Web Audio API) ---
let audioCtx = null;

function getAudioContext() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    return audioCtx;
}

function playSciFiSound(type) {
    try {
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);

        const now = ctx.currentTime;
        if (type === 'activate') {
            osc.frequency.setValueAtTime(440, now);
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.12);
            gain.gain.setValueAtTime(0.18, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
            osc.start(now);
            osc.stop(now + 0.15);
        } else if (type === 'transmit') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(500, now);
            osc.frequency.exponentialRampToValueAtTime(1100, now + 0.1);
            gain.gain.setValueAtTime(0.12, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
            osc.start(now);
            osc.stop(now + 0.12);
        } else if (type === 'tool') {
            osc.type = 'square';
            osc.frequency.setValueAtTime(700, now);
            osc.frequency.setValueAtTime(1000, now + 0.05);
            gain.gain.setValueAtTime(0.08, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
            osc.start(now);
            osc.stop(now + 0.08);
        }
    } catch (e) {}
}

// --- Speech Recognition (STT & Wake Word) ---
function initSpeechRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) return;

    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isRecording = true;
        setStatus("LISTENING");
        const micBtn = document.getElementById("micBtn");
        if (micBtn) micBtn.classList.add("recording");
        const micLabel = document.getElementById("micLabel");
        if (micLabel) micLabel.innerText = "LISTENING...";
    };

    recognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }

        const input = document.getElementById("commandInput");
        if (input) input.value = transcript;

        if (event.results[0].isFinal) {
            handleWakeWordAndSend(transcript);
        }
    };

    recognition.onerror = () => {
        resetVoiceUI();
    };

    recognition.onend = () => {
        resetVoiceUI();
    };
}

function handleWakeWordAndSend(transcript) {
    const lower = transcript.toLowerCase().trim();
    
    // Automatic Persona Switch on Wake Word
    if (lower.startsWith("hey jarvis") || lower.startsWith("jarvis")) {
        switchPersona("jarvis");
    } else if (lower.startsWith("hey friday") || lower.startsWith("friday")) {
        switchPersona("friday");
    } else if (lower.startsWith("ultron")) {
        switchPersona("ultron");
    } else if (lower.startsWith("hey tony") || lower.startsWith("tony")) {
        switchPersona("tony");
    }

    sendChatMessage(transcript);
}

function toggleVoiceInput() {
    stopSpeaking(); // Barge-in: immediately stop AI talking

    if (!recognition) initSpeechRecognition();
    if (!recognition) {
        alert("Speech Recognition is not supported by your browser. Please use Chrome, Edge, or Brave.");
        return;
    }

    if (isRecording) {
        recognition.stop();
        resetVoiceUI();
    } else {
        try {
            recognition.start();
        } catch (e) {
            resetVoiceUI();
        }
    }
}

function resetVoiceUI() {
    isRecording = false;
    const micBtn = document.getElementById("micBtn");
    if (micBtn) micBtn.classList.remove("recording");
    const micLabel = document.getElementById("micLabel");
    if (micLabel) micLabel.innerText = "PUSH TO SPEAK";
    if (currentState === "LISTENING") setStatus("STANDBY");
}

// --- Chat & Command Submissions ---
function handleInputKeydown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        handleCommandSubmit(event);
    }
}

function handleCommandSubmit(event) {
    if (event) event.preventDefault();
    const input = document.getElementById("commandInput");
    if (!input) return;
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    sendChatMessage(text);
}

function sendQuickPrompt(promptText) {
    sendChatMessage(promptText);
}

async function sendChatMessage(promptText) {
    stopSpeaking(); // Barge-in
    playSciFiSound("transmit");

    // Add User Message Card to UI
    appendMessageCard("user", promptText);
    setStatus("THINKING");

    const startTime = performance.now();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt: promptText,
                persona: currentPersona
            })
        });

        const data = await response.json();
        const latencySec = ((performance.now() - startTime) / 1000).toFixed(2);
        
        // Update latency badge
        const badge = document.getElementById("latencyBadge");
        if (badge) badge.innerText = `LATENCY: ${latencySec}s`;

        // Add AI Message Card
        appendMessageCard("ai", data.text || "Protocol executed, sir.", data.tool_calls, data.source);

        // Fast streaming TTS read-aloud
        if (data.text) {
            streamSpeakResponse(data.text);
        } else {
            setStatus("STANDBY");
        }

    } catch (err) {
        console.error("API error:", err);
        appendMessageCard("ai", "Communication relay failed. Local systems standing by.", []);
        setStatus("STANDBY");
    }
}

// --- UI Message Cards & Markdown ---
function appendMessageCard(sender, text, toolCalls = [], source = "") {
    const chatFeed = document.getElementById("chatFeed");
    if (!chatFeed) return;

    const config = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
    const card = document.createElement("div");
    card.className = `message-card ${sender === 'user' ? 'user-msg' : 'tony-msg'}`;

    const timeStr = new Date().toTimeString().split(" ")[0];
    const avatar = sender === 'user' ? '👤' : config.avatar;
    const name = sender === 'user' ? 'COMMANDER (YOU)' : `${config.name} CORE`;

    let toolsHtml = "";
    if (toolCalls && toolCalls.length > 0) {
        playSciFiSound("tool");
        toolsHtml = toolCalls.map(t => `<div class="tool-chip">⚡ <code>${t.tool}</code> executed</div>`).join("");
    }

    // Format markdown safely
    let formattedBody = text;
    if (window.marked && typeof window.marked.parse === "function") {
        try {
            formattedBody = window.marked.parse(text);
        } catch (e) {
            formattedBody = `<p>${escapeHtml(text)}</p>`;
        }
    } else {
        formattedBody = `<p>${escapeHtml(text)}</p>`;
    }

    card.innerHTML = `
        <div class="msg-header">
            <div class="sender-info">
                <span class="sender-avatar">${avatar}</span>
                <span class="sender-name">${name}</span>
            </div>
            <span class="msg-time">${timeStr}</span>
        </div>
        ${toolsHtml}
        <div class="msg-body markdown-content">${formattedBody}</div>
        ${sender === 'ai' ? `
        <div class="msg-actions">
            <button class="msg-btn" onclick="speakThisText(this)">🔊 Speak</button>
            <button class="msg-btn" onclick="copyCardContent(this)">📋 Copy</button>
        </div>` : ''}
    `;

    chatFeed.appendChild(card);
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function speakThisText(btn) {
    const card = btn.closest(".message-card");
    if (!card) return;
    const body = card.querySelector(".msg-body");
    if (body) streamSpeakResponse(body.innerText);
}

function speakLastResponse(btn) {
    speakThisText(btn);
}

function copyCardContent(btn) {
    const card = btn.closest(".message-card");
    if (!card) return;
    const body = card.querySelector(".msg-body");
    if (body) {
        navigator.clipboard.writeText(body.innerText);
        btn.innerText = "✓ Copied";
        setTimeout(() => { btn.innerText = "📋 Copy"; }, 1500);
    }
}

function clearChatThread() {
    const chatFeed = document.getElementById("chatFeed");
    if (chatFeed) {
        chatFeed.innerHTML = "";
        const config = PERSONA_CONFIGS[currentPersona];
        appendMessageCard("ai", config.greeting);
    }
}

// --- Tactical Quick Arsenal Triggers ---
function triggerAction(action) {
    if (action === 'diagnostics') {
        sendChatMessage("Run complete system telemetry scan and report status.");
    } else if (action === 'screen') {
        sendChatMessage("Analyze screen vision telemetry.");
    } else if (action === 'weather') {
        sendChatMessage("What is the current atmospheric weather?");
    } else if (action === 'status') {
        sendChatMessage("Give me a full status report on the Arc Reactor and our operational readiness.");
    } else if (action === 'volume_up') {
        sendChatMessage("Increase master system volume.");
    } else if (action === 'calc') {
        sendChatMessage("Open calculator application.");
    }
}

// --- Arc Reactor 3D/Canvas Visualizer ---
const canvas = document.getElementById("arcCanvas");
const ctx = canvas ? canvas.getContext("2d") : null;
let animAngle = 0;
let pulseVal = 0;

function setStatus(state) {
    currentState = state;
    const statusEl = document.getElementById("coreStatus");
    if (statusEl) statusEl.innerText = state;
}

function drawArcReactor() {
    if (!ctx || !canvas) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    const config = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
    const hexColor = config.color;

    // Adjust rotation speed based on state
    let speed = 0.02;
    if (currentState === "THINKING") speed = 0.08;
    else if (currentState === "SPEAKING") speed = 0.05;
    else if (currentState === "LISTENING") speed = 0.04;

    animAngle += speed;
    pulseVal += 0.04;

    // Outer Glow Circle
    const glowRad = 110 + Math.sin(pulseVal) * (currentState === "SPEAKING" ? 10 : 4);
    const grad = ctx.createRadialGradient(centerX, centerY, 20, centerX, centerY, glowRad);
    grad.addColorStop(0, hexColor + "88");
    grad.addColorStop(0.5, hexColor + "33");
    grad.addColorStop(1, "transparent");

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(centerX, centerY, glowRad, 0, Math.PI * 2);
    ctx.fill();

    // Outer Concentric Ring
    ctx.strokeStyle = hexColor;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, 105, 0, Math.PI * 2);
    ctx.stroke();

    // Rotating Segment Ring
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(animAngle);
    const segments = currentPersona === "ultron" ? 6 : (currentPersona === "friday" ? 8 : 10);
    for (let i = 0; i < segments; i++) {
        const theta = (i * Math.PI * 2) / segments;
        ctx.strokeStyle = hexColor;
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(0, 0, 85, theta, theta + 0.35);
        ctx.stroke();

        // Node dots
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(Math.cos(theta) * 85, Math.sin(theta) * 85, 3, 0, Math.PI * 2);
        ctx.fill();
    }
    ctx.restore();

    // Counter-Rotating Inner Ring
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(-animAngle * 1.5);
    ctx.strokeStyle = hexColor + "aa";
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 8]);
    ctx.beginPath();
    ctx.arc(0, 0, 60, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    // Core Pulse Node
    const coreRadius = 25 + Math.sin(pulseVal * 2) * (currentState === "SPEAKING" ? 6 : 2);
    const coreGrad = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, coreRadius);
    coreGrad.addColorStop(0, "#ffffff");
    coreGrad.addColorStop(0.4, hexColor);
    coreGrad.addColorStop(1, "transparent");

    ctx.fillStyle = coreGrad;
    ctx.beginPath();
    ctx.arc(centerX, centerY, coreRadius, 0, Math.PI * 2);
    ctx.fill();

    requestAnimationFrame(drawArcReactor);
}
if (canvas) drawArcReactor();

// --- Live Telemetry Polling ---
async function fetchTelemetry() {
    try {
        const res = await fetch("/api/telemetry");
        const data = await res.json();
        
        const cpuVal = document.getElementById("cpu-val");
        const cpuFill = document.getElementById("cpu-fill");
        if (cpuVal) cpuVal.innerText = `${data.cpu_usage_percent}%`;
        if (cpuFill) cpuFill.style.width = `${data.cpu_usage_percent}%`;

        const ramVal = document.getElementById("ram-val");
        const ramFill = document.getElementById("ram-fill");
        if (ramVal) ramVal.innerText = `${data.ram_percent}%`;
        if (ramFill) ramFill.style.width = `${data.ram_percent}%`;

        const batVal = document.getElementById("battery-val");
        if (batVal) batVal.innerText = data.battery_percent;
    } catch (e) {}
}
setInterval(fetchTelemetry, 3000);
fetchTelemetry();


// Auto-initialize default persona on load
window.addEventListener('DOMContentLoaded', () => {
    switchPersona('tony');
});
