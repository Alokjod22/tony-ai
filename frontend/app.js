// Tony AI HUD Controller & WebSocket Client

let ws = null;
let currentState = "STANDBY"; // STANDBY, LISTENING, THINKING, SPEAKING, EXECUTING
let isRecording = false;
let recognition = null;

// Initialize Clock
function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById("clock");
    if (clockEl) clockEl.innerText = now.toTimeString().split(" ")[0];
}
setInterval(updateClock, 1000);
updateClock();

// --- In-Browser Speech Synthesis (Tony's Voice) ---
function speakInBrowser(text) {
    if (!('speechSynthesis' in window)) return;
    try {
        window.speechSynthesis.cancel(); // Stop any pending speech
        const cleanText = text.replace(/[*#`_]/g, "").trim();
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.05;
        utterance.pitch = 0.95;

        // Select authentic British / refined Jarvis voice if available
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => 
            (v.lang === "en-GB" || v.name.includes("UK") || v.name.includes("British") || v.name.includes("Daniel") || v.name.includes("George") || v.name.includes("Arthur"))
        ) || voices.find(v => 
            (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("David") || v.name.includes("Male")) && v.lang.startsWith("en")
        );
        if (preferredVoice) utterance.voice = preferredVoice;
        utterance.rate = 1.0;
        utterance.pitch = 0.92;

        utterance.onstart = () => setStatus("SPEAKING");
        utterance.onend = () => setStatus("STANDBY");
        utterance.onerror = () => setStatus("STANDBY");

        window.speechSynthesis.speak(utterance);
    } catch (e) {
        console.warn("[TTS Error]:", e);
    }
}
// Pre-load voices
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
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.15);
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
            osc.start(now);
            osc.stop(now + 0.2);
        } else if (type === 'transmit') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(600, now);
            osc.frequency.exponentialRampToValueAtTime(1200, now + 0.1);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
            osc.start(now);
            osc.stop(now + 0.15);
        } else if (type === 'tool') {
            osc.type = 'square';
            osc.frequency.setValueAtTime(800, now);
            osc.frequency.setValueAtTime(1200, now + 0.05);
            gain.gain.setValueAtTime(0.1, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
            osc.start(now);
            osc.stop(now + 0.1);
        }
    } catch (e) {}
}

// --- Arc Reactor Canvas Visualizer ---
const canvas = document.getElementById("arcCanvas");
const ctx = canvas.getContext("2d");
let angle = 0;

function drawArcReactor() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    // Pulse size based on state
    let pulse = Math.sin(Date.now() / 250) * 4;
    let coreRadius = 35;
    let colorTheme = "#00f0ff";
    let glowColor = "rgba(0, 240, 255, ";

    if (currentState === "LISTENING") {
        colorTheme = "#ff3344";
        glowColor = "rgba(255, 51, 68, ";
        pulse = Math.sin(Date.now() / 120) * 8;
    } else if (currentState === "THINKING" || currentState === "EXECUTING") {
        colorTheme = "#ff9d00";
        glowColor = "rgba(255, 157, 0, ";
        pulse = Math.sin(Date.now() / 150) * 6;
    } else if (currentState === "SPEAKING") {
        colorTheme = "#00f5d4";
        glowColor = "rgba(0, 245, 212, ";
        pulse = Math.sin(Date.now() / 100) * 10;
    }

    // 1. Outer Hexagonal Shield Ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(-angle * 0.5);
    ctx.strokeStyle = glowColor + "0.3)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
        const rad = (i * 60 * Math.PI) / 180;
        const x = Math.cos(rad) * 155;
        const y = Math.sin(rad) * 155;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
    ctx.restore();

    // 2. Segmented Outer Gear Ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(angle);
    ctx.strokeStyle = colorTheme;
    ctx.lineWidth = 4;
    ctx.shadowBlur = 15;
    ctx.shadowColor = colorTheme;

    for (let i = 0; i < 12; i++) {
        ctx.beginPath();
        const startRad = (i * 30 * Math.PI) / 180;
        const endRad = startRad + (20 * Math.PI) / 180;
        ctx.arc(0, 0, 130 + pulse * 0.5, startRad, endRad);
        ctx.stroke();
    }
    ctx.restore();

    // 3. Counter-Rotating Inner Tech Ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(-angle * 1.5);
    ctx.strokeStyle = glowColor + "0.6)";
    ctx.lineWidth = 3;

    for (let i = 0; i < 8; i++) {
        ctx.beginPath();
        const startRad = (i * 45 * Math.PI) / 180;
        const endRad = startRad + (30 * Math.PI) / 180;
        ctx.arc(0, 0, 85, startRad, endRad);
        ctx.stroke();

        // Inner triangular power injectors
        const pX = Math.cos(startRad) * 75;
        const pY = Math.sin(startRad) * 75;
        ctx.fillStyle = colorTheme;
        ctx.beginPath();
        ctx.arc(pX, pY, 3, 0, Math.PI * 2);
        ctx.fill();
    }
    ctx.restore();

    // 4. Central Glowing Arc Core
    const grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, coreRadius + pulse);
    grad.addColorStop(0, "#ffffff");
    grad.addColorStop(0.4, colorTheme);
    grad.addColorStop(1, "transparent");

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, coreRadius + pulse, 0, Math.PI * 2);
    ctx.fill();

    // Inner Core Symbol (Triangle)
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(angle * 0.8);
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < 3; i++) {
        const rad = (i * 120 * Math.PI) / 180;
        const x = Math.cos(rad) * (coreRadius * 0.6);
        const y = Math.sin(rad) * (coreRadius * 0.6);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
    ctx.restore();

    angle += 0.015;
    requestAnimationFrame(drawArcReactor);
}
drawArcReactor();

// --- State Manager ---
function setStatus(state) {
    currentState = state;
    const statusEl = document.getElementById("coreStatus");
    if (statusEl) statusEl.innerText = state;
}

// --- WebSocket Connection ---
function initWebSocket() {
    const host = window.location.host || "127.0.0.1:8000";
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    try {
        ws = new WebSocket(`${protocol}//${host}/ws/stream`);

        ws.onopen = () => {
            console.log("[WS] Connected to Tony Core.");
            setStatus("ONLINE");
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleServerMessage(data);
            } catch (err) {
                console.warn("[WS Parse Error]:", err);
            }
        };

        ws.onclose = () => {
            console.warn("[WS] Disconnected. Reconnecting in 3s...");
            setTimeout(initWebSocket, 3000);
        };
    } catch (e) {
        console.warn("[WS Init Error]:", e);
    }
}
initWebSocket();

// Periodic fallback telemetry poll
setInterval(() => {
    fetch("/api/telemetry")
        .then(res => res.json())
        .then(data => updateTelemetry(data))
        .catch(() => {});
}, 3500);

function handleServerMessage(data) {
    if (data.type === "telemetry") {
        updateTelemetry(data.payload);
    } else if (data.type === "response") {
        removeTypingIndicator();
        setStatus("SPEAKING");
        addMessage("tony", data.payload.text);
        if (data.payload.tool_calls && data.payload.tool_calls.length > 0) {
            playSciFiSound("tool");
            data.payload.tool_calls.forEach(tc => {
                addMessage("tool", `[EXEC] ${tc.tool || tc.name}: ${JSON.stringify(tc.result || tc.args)}`);
            });
        }
        speakInBrowser(data.payload.text);
    } else if (data.type === "state_change") {
        setStatus(data.state);
    }
}

// Update Telemetry Panel
function updateTelemetry(diag) {
    if (!diag) return;
    const cpuVal = document.getElementById("cpu-val");
    const cpuFill = document.getElementById("cpu-fill");
    if (cpuVal) cpuVal.innerText = `${diag.cpu_usage_percent}%`;
    if (cpuFill) cpuFill.style.width = `${diag.cpu_usage_percent}%`;

    const ramVal = document.getElementById("ram-val");
    const ramFill = document.getElementById("ram-fill");
    if (ramVal) ramVal.innerText = `${diag.ram_percent}% (${diag.ram_used_gb} GB)`;
    if (ramFill) ramFill.style.width = `${diag.ram_percent}%`;

    const batVal = document.getElementById("battery-val");
    const batFill = document.getElementById("battery-fill");
    if (batVal) batVal.innerText = typeof diag.battery_percent === 'number' ? `${diag.battery_percent}%` : diag.battery_percent;
    if (batFill) batFill.style.width = typeof diag.battery_percent === 'number' ? `${diag.battery_percent}%` : '100%';

    const osVal = document.getElementById("os-val");
    if (osVal && diag.os) osVal.innerText = diag.os.toUpperCase();
}

// Chat Messages Feed
function addMessage(role, text) {
    const feed = document.getElementById("chatFeed");
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const sender = document.createElement("span");
    sender.className = "sender";
    sender.innerText = role === "tony" ? "TONY:" : (role === "user" ? "YOU:" : "SYSTEM LOG:");

    const p = document.createElement("p");
    p.innerText = text;

    div.appendChild(sender);
    div.appendChild(p);
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
}

function showTypingIndicator() {
    removeTypingIndicator();
    const feed = document.getElementById("chatFeed");
    const div = document.createElement("div");
    div.id = "typingIndicator";
    div.className = "message tony";
    div.innerHTML = `<span class="sender">TONY:</span><p style="color:#00f0ff;font-style:italic;">Processing tactical cognitive analysis...</p>`;
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
}

function removeTypingIndicator() {
    const ind = document.getElementById("typingIndicator");
    if (ind) ind.remove();
}

// Command Submission
function handleCommandSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("commandInput");
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    sendPrompt(text);
}

async function sendPrompt(text) {
    addMessage("user", text);
    playSciFiSound("transmit");
    setStatus("THINKING");
    showTypingIndicator();

    try {
        // Use direct HTTP fetch for 100% reliable responses
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: text })
        });
        
        if (!res.ok) {
            throw new Error(`Server returned ${res.status}`);
        }
        
        const data = await res.json();
        handleServerMessage({ type: "response", payload: data });
    } catch (err) {
        removeTypingIndicator();
        console.error("Chat Error:", err);
        addMessage("tony", `Communication error: ${err.message}. Retrying link...`);
        setStatus("STANDBY");
    }
}

// Quick Arsenal Actions
function triggerAction(action) {
    playSciFiSound("tool");
    const actionPrompts = {
        diagnostics: "Run a full system diagnostic scan and report CPU, RAM, and battery metrics.",
        screen: "What is currently on my screen? Give me a quick summary.",
        calc: "Open calculator application.",
        notes: "Open notepad.",
        weather: "What is the current weather forecast?",
        volume_up: "Increase volume."
    };
    if (actionPrompts[action]) {
        sendPrompt(actionPrompts[action]);
    }
}

// Browser Web Speech API Voice Recognition
function toggleVoiceInput() {
    if (isRecording) {
        stopVoiceInput();
    } else {
        startVoiceInput();
    }
}

function startVoiceInput() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
        alert("Browser Speech Recognition not supported in this browser. Please type in the transmit box.");
        return;
    }

    try {
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onstart = () => {
            isRecording = true;
            setStatus("LISTENING");
            document.getElementById("micBtn").classList.add("active");
            document.getElementById("micLabel").innerText = "LISTENING... SPEAK NOW";
            playSciFiSound("activate");
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            stopVoiceInput();
            sendPrompt(transcript);
        };

        recognition.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            stopVoiceInput();
        };

        recognition.onend = () => {
            stopVoiceInput();
        };

        recognition.start();
    } catch (e) {
        console.warn("Speech start error:", e);
        stopVoiceInput();
    }
}

function stopVoiceInput() {
    isRecording = false;
    const btn = document.getElementById("micBtn");
    const lbl = document.getElementById("micLabel");
    if (btn) btn.classList.remove("active");
    if (lbl) lbl.innerText = "PUSH TO ENGAGE VOICE";
    if (currentState === "LISTENING") {
        setStatus("STANDBY");
    }
    if (recognition) {
        try { recognition.stop(); } catch(e) {}
    }
}
