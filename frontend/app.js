// Tony AI HUD Controller & WebSocket Client

let ws = null;
let currentState = "STANDBY"; // STANDBY, LISTENING, THINKING, SPEAKING, EXECUTING
let isRecording = false;
let recognition = null;

// Initialize Clock
function updateClock() {
    const now = new Date();
    document.getElementById("clock").innerText = now.toTimeString().split(" ")[0];
}
setInterval(updateClock, 1000);
updateClock();

// --- Sci-Fi Audio Synthesizer (Web Audio API) ---
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playSciFiSound(type) {
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    const now = audioCtx.currentTime;
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
    document.getElementById("coreStatus").innerText = state;
}

// --- WebSocket Connection ---
function initWebSocket() {
    const host = window.location.host || "127.0.0.1:8000";
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${protocol}//${host}/ws/stream`);

    ws.onopen = () => {
        console.log("[WS] Connected to Tony Core.");
        setStatus("ONLINE");
        playSciFiSound("activate");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleServerMessage(data);
    };

    ws.onclose = () => {
        console.warn("[WS] Connection lost. Reconnecting in 3s...");
        setStatus("OFFLINE");
        setTimeout(initWebSocket, 3000);
    };
}
initWebSocket();

function handleServerMessage(data) {
    if (data.type === "telemetry") {
        updateTelemetry(data.payload);
    } else if (data.type === "response") {
        setStatus("SPEAKING");
        addMessage("tony", data.payload.text);
        if (data.payload.tool_calls && data.payload.tool_calls.length > 0) {
            playSciFiSound("tool");
            data.payload.tool_calls.forEach(tc => {
                addMessage("tool", `[EXEC] ${tc.tool || tc.name}: ${JSON.stringify(tc.result || tc.args)}`);
            });
        }
        setTimeout(() => setStatus("STANDBY"), 3000);
    } else if (data.type === "state_change") {
        setStatus(data.state);
    }
}

// Update Telemetry Panel
function updateTelemetry(diag) {
    if (!diag) return;
    document.getElementById("cpu-val").innerText = `${diag.cpu_usage_percent}%`;
    document.getElementById("cpu-fill").style.width = `${diag.cpu_usage_percent}%`;

    document.getElementById("ram-val").innerText = `${diag.ram_percent}% (${diag.ram_used_gb} GB)`;
    document.getElementById("ram-fill").style.width = `${diag.ram_percent}%`;

    document.getElementById("battery-val").innerText = typeof diag.battery_percent === 'number' ? `${diag.battery_percent}%` : diag.battery_percent;
    document.getElementById("battery-fill").style.width = typeof diag.battery_percent === 'number' ? `${diag.battery_percent}%` : '100%';

    document.getElementById("os-val").innerText = diag.os.toUpperCase();
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

// Command Submission
function handleCommandSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("commandInput");
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    sendPrompt(text);
}

function sendPrompt(text) {
    addMessage("user", text);
    playSciFiSound("transmit");
    setStatus("THINKING");

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "prompt", text: text }));
    } else {
        // Fallback HTTP POST
        fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: text })
        })
        .then(res => res.json())
        .then(data => {
            handleServerMessage({ type: "response", payload: data });
        });
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
        alert("Browser Speech Recognition not supported. Use the backend microphone or text console.");
        return;
    }

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
        console.error("Speech Error:", event.error);
        stopVoiceInput();
    };

    recognition.onend = () => {
        stopVoiceInput();
    };

    recognition.start();
}

function stopVoiceInput() {
    isRecording = false;
    document.getElementById("micBtn").classList.remove("active");
    document.getElementById("micLabel").innerText = "PUSH TO ENGAGE VOICE";
    if (currentState === "LISTENING") {
        setStatus("STANDBY");
    }
    if (recognition) {
        try { recognition.stop(); } catch(e) {}
    }
}
