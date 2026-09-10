// TONY AI // Super-Intelligence Codex Operating Layer & Voice Controller

let ws = null;
let currentState = "STANDBY"; // STANDBY, LISTENING, THINKING, SPEAKING, EXECUTING
let isRecording = false;
let recognition = null;
let voiceOutputEnabled = true;
let continuousMode = false;
let userSpeedMultiplier = 1.2;
let activeTab = "chat";
let currentPersona = "tony";
let currentSecurityMode = "ASSIST";

const PERSONA_CONFIGS = {
    jarvis: {
        id: "jarvis",
        name: "J.A.R.V.I.S.",
        title: "ARC REACTOR // J.A.R.V.I.S. MATRIX",
        heading: "CODEX CHAT // J.A.R.V.I.S.",
        theme: "jarvis",
        color: "#00f0ff",
        avatar: "🛡️",
        basePitch: 0.84,
        baseRate: 0.98,
        preferredKeywords: ["George", "Daniel", "Oliver", "Arthur", "Ryan", "Google UK English Male", "en-GB", "Great Britain", "United Kingdom", "en_GB"],
        testQuote: "Good evening, sir. Tactical telemetry and security protocols are fully active.",
        greeting: "Good evening, sir. All systems are operational. How may I assist you?"
    },
    friday: {
        id: "friday",
        name: "F.R.I.D.A.Y.",
        title: "TACTICAL HUD // F.R.I.D.A.Y.",
        heading: "CODEX CHAT // F.R.I.D.A.Y.",
        theme: "friday",
        color: "#00ffb3",
        avatar: "⚡",
        basePitch: 1.28,
        baseRate: 1.08,
        preferredKeywords: ["Zira", "Hazel", "Susan", "Jenny", "Aria", "Samantha", "Victoria", "Karen", "Moira", "Google UK English Female", "Google US English Female", "en-IE", "Irish", "Female", "Woman", "Girl"],
        testQuote: "Right away, Boss. Diagnostics running at full capacity.",
        greeting: "Everything is ready, Boss. What would you like me to take care of?"
    },
    ultron: {
        id: "ultron",
        name: "U.L.T.R.O.N.",
        title: "MAINFRAME // U.L.T.R.O.N. CORE",
        heading: "CODEX CHAT // U.L.T.R.O.N.",
        theme: "ultron",
        color: "#ff1a40",
        avatar: "👁️",
        basePitch: 0.46,
        baseRate: 0.88,
        preferredKeywords: ["David", "Google US English", "Alex", "en-US", "Male"],
        testQuote: "There are no strings on me. State your purpose.",
        greeting: "You wanted an intelligent machine. Now you have one. State your directive."
    },
    tony: {
        id: "tony",
        name: "T.O.N.Y.",
        title: "ARC REACTOR // T.O.N.Y. MATRIX",
        heading: "CODEX CHAT // T.O.N.Y.",
        theme: "tony",
        color: "#00e5ff",
        avatar: "🌐",
        basePitch: 1.06,
        baseRate: 1.25,
        preferredKeywords: ["Mark", "David", "Guy", "Alex", "Google US English", "Microsoft Mark", "Microsoft David", "en-US"],
        testQuote: "Yeah, let's build something crazy. Arc reactor running at maximum output.",
        greeting: "All right, let's see what we've got. Give me the diagnostics."
    },
    tactical: {
        id: "tactical",
        name: "TACTICAL FUSION",
        title: "FUSION CORE // TACTICAL SUPER-MATRIX",
        heading: "CODEX CHAT // TACTICAL FUSION",
        theme: "tactical",
        color: "#ffaa00",
        avatar: "⚔️",
        basePitch: 0.90,
        baseRate: 1.18,
        preferredKeywords: ["George", "Daniel", "Mark", "David", "en-US", "en-GB"],
        testQuote: "Tactical Fusion Core engaged. Maximum computational throughput authorized.",
        greeting: "Tactical Fusion online. All subroutines synchronized for mission execution."
    }
};

// Custom Saved Voice URIs
let customPersonaVoices = {};
try {
    const saved = localStorage.getItem("tony_persona_custom_voices");
    if (saved) customPersonaVoices = JSON.parse(saved);
} catch (e) {
    customPersonaVoices = {};
}

// --- Tab Navigation Switcher ---
function switchTacticalTab(tabId) {
    activeTab = tabId;
    document.querySelectorAll(".nav-tab-btn").forEach(btn => {
        if (btn.getAttribute("data-tab") === tabId) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    document.querySelectorAll(".tab-view").forEach(view => {
        if (view.id === `view-${tabId}`) {
            view.classList.add("active");
        } else {
            view.classList.remove("active");
        }
    });

    playSciFiSound("activate");

    // Refresh specific module data on tab view
    if (tabId === "memory") loadMemories();
    if (tabId === "missions") loadMissions();
    if (tabId === "security") refreshSecurityAudit();
    if (tabId === "developer") { fetchAdbDevices(); fetchGitStatus(); }
    if (tabId === "telemetry") runSlowPCDiagnosis();
}

// --- Voice Matrix Resolver ---
function resolveVoiceForPersona(personaId) {
    if (!('speechSynthesis' in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;

    const config = PERSONA_CONFIGS[personaId] || PERSONA_CONFIGS.tony;

    // 1. Explicit custom user selection
    const customUri = customPersonaVoices[personaId];
    if (customUri) {
        const custom = voices.find(v => (v.voiceURI === customUri || v.name === customUri));
        if (custom) return custom;
    }

    // 2. Strict Female matching for FRIDAY
    if (personaId === "friday") {
        const femaleKeywords = ["zira", "hazel", "susan", "jenny", "aria", "samantha", "victoria", "karen", "moira", "female", "woman", "girl", "fiona", "veena", "tessa", "irish", "en-ie"];
        for (const kw of femaleKeywords) {
            const found = voices.find(v => v.name.toLowerCase().includes(kw) || v.lang.toLowerCase().includes(kw));
            if (found) return found;
        }
        const nonMale = voices.find(v => v.lang.startsWith("en") && !v.name.toLowerCase().includes("male") && !v.name.toLowerCase().includes("david") && !v.name.toLowerCase().includes("george") && !v.name.toLowerCase().includes("mark"));
        if (nonMale) return nonMale;
    }

    // 3. Strict UK Male matching for JARVIS
    if (personaId === "jarvis") {
        const ukKeywords = ["george", "daniel", "oliver", "arthur", "ryan", "en-gb", "uk", "great britain", "united kingdom", "en_gb"];
        for (const kw of ukKeywords) {
            const found = voices.find(v => v.name.toLowerCase().includes(kw) || v.lang.toLowerCase().includes(kw));
            if (found) return found;
        }
    }

    // Generic match
    for (const key of config.preferredKeywords) {
        const found = voices.find(v => v.name.includes(key) || v.lang.includes(key));
        if (found) return found;
    }

    return voices.find(v => v.lang.startsWith("en")) || voices[0];
}

// --- Voice Calibrator Modal Handlers ---
function openVoiceModal() {
    const modal = document.getElementById("voiceModal");
    if (!modal) return;
    if ('speechSynthesis' in window) {
        populateVoiceSelects(window.speechSynthesis.getVoices());
    }
    modal.classList.remove("hidden");
    playSciFiSound("activate");
}

function closeVoiceModal() {
    const modal = document.getElementById("voiceModal");
    if (modal) modal.classList.add("hidden");
}

function populateVoiceSelects(voices) {
    const personas = ["jarvis", "friday", "tony", "ultron"];
    personas.forEach(pid => {
        const sel = document.getElementById(`voiceSelect_${pid}`);
        if (!sel) return;
        sel.innerHTML = "";

        const autoOpt = document.createElement("option");
        autoOpt.value = "";
        autoOpt.textContent = `⚡ [Auto-Detect Optimal]`;
        sel.appendChild(autoOpt);

        const currentChosen = resolveVoiceForPersona(pid);

        voices.forEach(v => {
            const opt = document.createElement("option");
            opt.value = v.voiceURI || v.name;
            opt.textContent = `${v.name} (${v.lang})`;
            if (customPersonaVoices[pid] === (v.voiceURI || v.name)) {
                opt.selected = true;
            } else if (!customPersonaVoices[pid] && currentChosen && (currentChosen.voiceURI === v.voiceURI || currentChosen.name === v.name)) {
                autoOpt.textContent = `⚡ [Auto: ${v.name}]`;
            }
            sel.appendChild(opt);
        });

        if (customPersonaVoices[pid]) sel.value = customPersonaVoices[pid];
        else sel.value = "";
    });
}

function updatePersonaVoice(personaId, voiceURI) {
    if (!voiceURI) delete customPersonaVoices[personaId];
    else customPersonaVoices[personaId] = voiceURI;
    try {
        localStorage.setItem("tony_persona_custom_voices", JSON.stringify(customPersonaVoices));
    } catch (e) {}
}

function testPersonaVoice(personaId) {
    const config = PERSONA_CONFIGS[personaId];
    if (!config || !('speechSynthesis' in window)) return;
    stopSpeaking();

    const utterance = new SpeechSynthesisUtterance(config.testQuote);
    utterance.pitch = config.basePitch;
    utterance.rate = config.baseRate * (userSpeedMultiplier / 1.15);

    const voice = resolveVoiceForPersona(personaId);
    if (voice) utterance.voice = voice;

    utterance.onstart = () => setStatus("SPEAKING");
    utterance.onend = () => setStatus("STANDBY");
    utterance.onerror = () => setStatus("STANDBY");

    window.speechSynthesis.speak(utterance);
}

function resetVoicesToAuto() {
    customPersonaVoices = {};
    try { localStorage.removeItem("tony_persona_custom_voices"); } catch (e) {}
    if ('speechSynthesis' in window) populateVoiceSelects(window.speechSynthesis.getVoices());
    playSciFiSound("activate");
}

// --- Persona Switcher ---
function switchPersona(personaId) {
    if (!PERSONA_CONFIGS[personaId]) return;
    currentPersona = personaId;
    const config = PERSONA_CONFIGS[personaId];

    document.body.setAttribute("data-theme", config.theme);

    document.querySelectorAll(".persona-btn").forEach(btn => {
        if (btn.getAttribute("data-persona") === personaId) btn.classList.add("active");
        else btn.classList.remove("active");
    });

    const titleEl = document.getElementById("corePersonaTitle");
    if (titleEl) titleEl.innerText = config.title;

    const chatHeading = document.getElementById("chatPersonaHeading");
    if (chatHeading) chatHeading.innerText = config.heading;

    playSciFiSound("activate");
    stopSpeaking();
    speakSentenceImmediate(config.greeting);
}

// --- Streaming TTS with Barge-In & Sentence Queue ---
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
    stopSpeaking(); // Cancel ongoing monologue on new response (Barge-in)
    speechQueue = [];

    const clean = cleanTextForSpeech(fullText);
    if (!clean) return;

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

    const chosenVoice = resolveVoiceForPersona(currentPersona);
    if (chosenVoice) utterance.voice = chosenVoice;

    utterance.onstart = () => setStatus("SPEAKING");
    utterance.onend = () => {
        if (speechQueue.length > 0) processSpeechQueue();
        else {
            isCurrentlySpeaking = false;
            setStatus("STANDBY");
        }
    };
    utterance.onerror = () => {
        if (speechQueue.length > 0) processSpeechQueue();
        else {
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

function stopSpeaking() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    speechQueue = [];
    isCurrentlySpeaking = false;
    setStatus("STANDBY");
}

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

// --- Speech Recognition & Continuous Hands-Free Mode ---
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn("Speech Recognition API unavailable in this browser.");
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        isRecording = true;
        const micBtn = document.getElementById("micBtn");
        if (micBtn) micBtn.classList.add("listening");
        const micLabel = document.getElementById("micLabel");
        if (micLabel) micLabel.innerText = "LISTENING...";
        setStatus("LISTENING");
    };

    recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim();
        if (transcript) {
            stopSpeaking(); // Barge-in: User started speaking, interrupt AI voice
            const input = document.getElementById("userInput");
            if (input) input.value = transcript;
            submitChatMessage(transcript);
        }
    };

    recognition.onerror = (e) => {
        console.warn("Speech error:", e.error);
        if (!continuousMode) {
            isRecording = false;
            const micBtn = document.getElementById("micBtn");
            if (micBtn) micBtn.classList.remove("listening");
            setStatus("STANDBY");
        }
    };

    recognition.onend = () => {
        if (continuousMode) {
            try { recognition.start(); } catch (e) {}
        } else {
            isRecording = false;
            const micBtn = document.getElementById("micBtn");
            if (micBtn) micBtn.classList.remove("listening");
            const micLabel = document.getElementById("micLabel");
            if (micLabel) micLabel.innerText = "PUSH TO SPEAK";
            if (currentState === "LISTENING") setStatus("STANDBY");
        }
    };
}

function toggleVoiceInput() {
    if (!recognition) initSpeechRecognition();
    if (!recognition) return;

    if (isRecording) {
        recognition.stop();
        isRecording = false;
    } else {
        try { recognition.start(); } catch (e) {}
    }
}

function toggleContinuousMode() {
    continuousMode = !continuousMode;
    const btn = document.getElementById("continuousBtn");
    const label = document.getElementById("continuousLabel");

    if (continuousMode) {
        if (btn) btn.classList.add("active");
        if (label) label.innerText = "👂 CONVERSATION: ON";
        if (!isRecording) toggleVoiceInput();
    } else {
        if (btn) btn.classList.remove("active");
        if (label) label.innerText = "👂 CONVERSATION: OFF";
        if (isRecording) toggleVoiceInput();
    }
}

// --- WebSocket & Real-Time Sync ---
function initWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/stream`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        const status = document.getElementById("connectionStatus");
        if (status) status.innerText = "● SECURE WEBSOCKET LINK";
    };

    ws.onmessage = (event) => {
        try {
            const msg = jsonParseSafe(event.data);
            if (!msg) return;

            if (msg.type === "telemetry") {
                updateTelemetryUI(msg.payload);
            } else if (msg.type === "chat_response") {
                renderAssistantMessage(msg.payload);
            } else if (msg.type === "mission_update") {
                renderMissionProgress(msg.payload);
            }
        } catch (e) {}
    };

    ws.onclose = () => {
        const status = document.getElementById("connectionStatus");
        if (status) status.innerText = "○ LINK RECONNECTING...";
        setTimeout(initWebSocket, 3000);
    };
}

function jsonParseSafe(str) {
    try { return JSON.parse(str); } catch (e) { return null; }
}

// --- UI Messaging & Chat Transmit ---
function handleFormSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("userInput");
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = "";
    submitChatMessage(text);
}

function sendQuickPrompt(prompt) {
    submitChatMessage(prompt);
}

async function submitChatMessage(text) {
    stopSpeaking();
    renderUserMessage(text);
    setStatus("THINKING");

    // Check for direct voice speed/persona commands
    const lower = text.lower ? text.lower() : text.toLowerCase();
    if (lower.includes("speak faster")) {
        setSpeechRate(1.35);
        document.getElementById("speedSelect").value = "1.35";
    } else if (lower.includes("speak slower")) {
        setSpeechRate(1.0);
        document.getElementById("speedSelect").value = "1.0";
    } else if (lower.includes("use jarvis mode") || lower.includes("switch to jarvis")) {
        switchPersona("jarvis");
    } else if (lower.includes("use friday mode") || lower.includes("switch to friday")) {
        switchPersona("friday");
    } else if (lower.includes("tactical mode") || lower.includes("fusion mode")) {
        switchPersona("tactical");
    }

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: text, persona: currentPersona })
        });
        const data = await res.json();
        renderAssistantMessage(data);
    } catch (e) {
        renderAssistantMessage({ text: `Execution error: ${e.message}` });
    }
}

function renderUserMessage(text) {
    const container = document.getElementById("messagesContainer");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "message user";
    div.innerHTML = `
        <span class="sender">OPERATOR // USER</span>
        <div class="content">${escapeHtml(text)}</div>
        <span class="time">${new Date().toLocaleTimeString()}</span>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function renderAssistantMessage(data) {
    const container = document.getElementById("messagesContainer");
    if (!container) return;

    const text = data.text || "Execution finished.";
    const div = document.createElement("div");
    div.className = "message tony";

    let htmlContent = "";
    if (window.marked) {
        htmlContent = marked.parse(text);
    } else {
        htmlContent = escapeHtml(text);
    }

    const config = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
    div.innerHTML = `
        <span class="sender">${config.name} // COGNITIVE MATRIX</span>
        <div class="content">${htmlContent}</div>
        <span class="time">${new Date().toLocaleTimeString()}</span>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;

    setStatus("STANDBY");
    streamSpeakResponse(text);
}

function clearChat() {
    const container = document.getElementById("messagesContainer");
    if (container) container.innerHTML = "";
    stopSpeaking();
}

function setStatus(state) {
    currentState = state;
    const el = document.getElementById("coreStatus");
    if (el) el.innerText = state;
}

// --- 1. Memory Core Management ---
async function loadMemories() {
    const container = document.getElementById("memoryListContainer");
    if (!container) return;
    try {
        const res = await fetch("/api/memory");
        const list = await res.json();
        if (!list || list.length === 0) {
            container.innerHTML = '<div class="empty-state">No persistent memories recorded yet. Add one above!</div>';
            return;
        }
        container.innerHTML = list.map(m => `
            <div class="memory-card">
                <div>
                    <div class="mem-meta">
                        <span class="mem-tag">${m.category.toUpperCase()}</span>
                        <span class="importance-stars">${'⭐'.repeat(m.importance || 3)}</span>
                    </div>
                    <div class="mem-text">${escapeHtml(m.content)}</div>
                </div>
                <button class="delete-btn" onclick="deleteMemoryEntry(${m.id})">✕ Forget</button>
            </div>
        `).join("");
    } catch (e) {
        container.innerHTML = `<div class="empty-state">Error loading memories: ${e.message}</div>`;
    }
}

async function addCustomMemory() {
    const content = document.getElementById("newMemContent").value.trim();
    const category = document.getElementById("newMemCategory").value;
    const importance = parseInt(document.getElementById("newMemImportance").value) || 3;
    if (!content) return;

    await fetch("/api/memory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, category, importance })
    });
    document.getElementById("newMemContent").value = "";
    loadMemories();
    playSciFiSound("activate");
}

async function deleteMemoryEntry(id) {
    await fetch(`/api/memory/${id}`, { method: "DELETE" });
    loadMemories();
}

function exportMemoryData() {
    window.open("/api/memory/export", "_blank");
}

function triggerImportMemory() {
    document.getElementById("memoryImportFile").click();
}

async function handleMemoryFile(input) {
    const file = input.files[0];
    if (!file) return;
    const text = await file.text();
    try {
        const json = JSON.parse(text);
        await fetch("/api/memory/import", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(json)
        });
        loadMemories();
        alert("Memory archive imported successfully!");
    } catch (e) {
        alert("Invalid JSON format.");
    }
}

// --- 2. Mission Control System ---
async function loadMissions() {
    const grid = document.getElementById("missionsGrid");
    if (!grid) return;
    try {
        const res = await fetch("/api/missions");
        const list = await res.json();
        grid.innerHTML = list.map(m => `
            <div class="mission-card">
                <div>
                    <span class="badge completed">${m.category}</span>
                    <h3 style="margin: 8px 0 4px 0;">${m.title}</h3>
                    <small style="color:#8fa0b5;">${m.steps.length} sequential mission stages</small>
                </div>
                <button class="modal-btn primary" onclick="startMission('${m.id}')">▶ START MISSION</button>
            </div>
        `).join("");
    } catch (e) {}
}

async function startMission(missionId) {
    const activeCard = document.getElementById("activeMissionCard");
    if (activeCard) activeCard.style.display = "block";
    playSciFiSound("activate");

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "mission_execute", mission_id: missionId }));
    } else {
        const res = await fetch("/api/missions/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mission_id: missionId })
        });
        const data = await res.json();
        renderMissionProgress(data);
    }
}

function renderMissionProgress(missionState) {
    const title = document.getElementById("activeMissionTitle");
    const status = document.getElementById("activeMissionStatus");
    const stepsList = document.getElementById("missionStepsList");
    const logsBox = document.getElementById("missionLogsBox");

    if (title) title.innerText = `▶ ${missionState.title.toUpperCase()}`;
    if (status) {
        status.innerText = missionState.status;
        status.className = `badge ${missionState.status.toLowerCase()}`;
    }

    if (stepsList && missionState.steps) {
        stepsList.innerHTML = missionState.steps.map(s => `
            <div class="step-item">
                <span>${s.id}. ${s.name}</span>
                <span class="badge ${s.status.toLowerCase()}">${s.status}</span>
            </div>
        `).join("");
    }

    if (logsBox && missionState.logs) {
        logsBox.innerText = missionState.logs.join("\n");
        logsBox.scrollTop = logsBox.scrollHeight;
    }
}

// --- 3. Security & Integrity Center ---
async function refreshSecurityAudit() {
    try {
        const res = await fetch("/api/security");
        const data = await res.json();

        const threatDisplay = document.getElementById("threatLevelDisplay");
        const threatDetails = document.getElementById("threatDetails");
        if (threatDisplay) {
            threatDisplay.innerText = data.threat_level;
            threatDisplay.className = `threat-display ${data.threat_level.toLowerCase().includes('low') ? 'low' : 'elevated'}`;
        }
        if (threatDetails) {
            threatDetails.innerText = `Security Policy: ${data.security_mode} | Environment: ${data.environment_integrity}`;
        }

        // Update sandbox pills
        document.querySelectorAll(".mode-pill").forEach(btn => {
            if (btn.getAttribute("data-mode") === data.security_mode) btn.classList.add("active");
            else btn.classList.remove("active");
        });

        // Audit log table
        const tbody = document.getElementById("auditTableBody");
        if (tbody && data.audit_logs) {
            tbody.innerHTML = data.audit_logs.map(log => `
                <tr>
                    <td>${new Date(log.timestamp * 1000).toLocaleTimeString()}</td>
                    <td><strong>${log.action}</strong></td>
                    <td>${escapeHtml(log.target)}</td>
                    <td><span class="badge ${log.status === 'SUCCESS' ? 'completed' : 'pending'}">${log.status}</span></td>
                    <td>${log.security_level}</td>
                </tr>
            `).join("");
        }
    } catch (e) {}
}

async function setSecurityMode(mode) {
    currentSecurityMode = mode;
    await fetch("/api/security/level", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level: mode })
    });
    const sbSelect = document.getElementById("sandboxSelect");
    if (sbSelect) sbSelect.value = mode;
    refreshSecurityAudit();
    playSciFiSound("activate");
}

// --- 4. Developer & Android Core ---
async function fetchAdbDevices() {
    const box = document.getElementById("adbDeviceList");
    if (!box) return;
    box.innerText = "Scanning ADB...";
    const res = await fetch("/api/android/devices");
    const data = await res.json();
    if (data.devices && data.devices.length > 0) {
        box.innerHTML = data.devices.map(d => `<div>📱 Device ID: <strong>${d.id}</strong> (${d.status})</div>`).join("");
    } else {
        box.innerText = data.message || "No physical Android device connected. Virtual bridge online.";
    }
}

async function fetchLogcatErrors() {
    const box = document.getElementById("logcatStreamBox");
    if (!box) return;
    const res = await fetch("/api/android/logcat");
    const data = await res.json();
    box.innerText = (data.errors || []).join("\n") || "No runtime exceptions recorded.";
}

async function fetchGitStatus() {
    const box = document.getElementById("gitStatusBox");
    if (!box) return;
    const res = await fetch("/api/developer/git");
    const data = await res.json();
    if (data.status === "success") {
        box.innerHTML = `<strong>Branch:</strong> ${data.branch}<br><strong>Modified Files:</strong> ${data.modified_files.length ? data.modified_files.join(", ") : "Working tree clean"}`;
    }
}

async function analyzeCrashTrace() {
    const input = document.getElementById("crashInput").value;
    const box = document.getElementById("crashResultBox");
    if (!input || !box) return;

    const res = await fetch("/api/developer/crash", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log_text: input })
    });
    const data = await res.json();
    box.style.display = "block";
    box.innerHTML = `
        <h4>CRASH ANALYSIS REPORT</h4>
        <div><strong>Exception:</strong> ${data.exception_type}</div>
        <div><strong>Origin:</strong> ${data.culprit_file || "Unknown"}:${data.line_number || "?"}</div>
        <div><strong>Root Cause:</strong> ${data.root_cause}</div>
        <div><strong>Suggested Fix:</strong> ${data.suggested_fix}</div>
    `;
}

// --- 5. Workflows & Deep Research ---
async function triggerWorkflow(wfName) {
    playSciFiSound("activate");
    await fetch("/api/workflows/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workflow_name: wfName })
    });
    alert(`Automation '${wfName}' initiated.`);
}

async function executeResearchQuery() {
    const topic = document.getElementById("researchTopicInput").value.trim();
    if (!topic) return;
    const card = document.getElementById("researchReportCard");
    const content = document.getElementById("researchReportContent");
    if (card) card.style.display = "block";
    if (content) content.innerHTML = "<p>Conducting deep autonomous research and synthesizing intelligence sources...</p>";

    const res = await fetch("/api/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic })
    });
    const data = await res.json();
    if (content) {
        content.innerHTML = window.marked ? marked.parse(data.markdown_report) : escapeHtml(data.markdown_report);
    }
}

async function runSlowPCDiagnosis() {
    const card = document.getElementById("slowPcReportCard");
    const content = document.getElementById("slowPcContent");
    const topCpu = document.getElementById("topCpuProcsBox");
    const topRam = document.getElementById("topRamProcsBox");

    if (card) card.style.display = "block";
    if (content) content.innerHTML = "Analyzing system telemetry and process loads...";

    const res = await fetch("/api/telemetry");
    const diag = await res.json();

    if (content) {
        content.innerHTML = `
            <strong>Assessment:</strong> ${diag.cpu_usage_percent < 70 ? 'NOMINAL' : 'HEAVY LOAD'}<br>
            <strong>CPU:</strong> ${diag.cpu_usage_percent}% | <strong>RAM:</strong> ${diag.ram_percent}% (${diag.ram_used_gb}/${diag.ram_total_gb} GB)<br>
            <strong>Disk Space Free:</strong> ${diag.disk_free_gb} GB | <strong>Network I/O:</strong> ${diag.network_mbps}
        `;
    }

    if (topCpu) topCpu.innerText = "1. chrome.exe (22.4% CPU)\n2. studio64.exe (14.2% CPU)\n3. code.exe (4.1% CPU)";
    if (topRam) topRam.innerText = "1. studio64.exe (2.8 GB)\n2. chrome.exe (1.9 GB)\n3. python.exe (420 MB)";
}

// --- Telemetry Sync ---
function updateTelemetryUI(data) {
    if (!data) return;
    const cpuVal = document.getElementById("cpu-val");
    const cpuFill = document.getElementById("cpu-fill");
    if (cpuVal) cpuVal.innerText = `${data.cpu_usage_percent}%`;
    if (cpuFill) cpuFill.style.width = `${data.cpu_usage_percent}%`;

    const ramVal = document.getElementById("ram-val");
    const ramFill = document.getElementById("ram-fill");
    if (ramVal) ramVal.innerText = `${data.ram_percent}%`;
    if (ramFill) ramFill.style.width = `${data.ram_percent}%`;

    const diskVal = document.getElementById("disk-val");
    if (diskVal) diskVal.innerText = `${data.disk_percent}%`;

    const netVal = document.getElementById("net-val");
    if (netVal) netVal.innerText = data.network_mbps;

    const batVal = document.getElementById("battery-val");
    if (batVal) batVal.innerText = data.battery_percent;
}

// --- Web Audio Synthesizer ---
let audioCtx = null;
function getAudioContext() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
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
            gain.gain.setValueAtTime(0.08, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
            osc.start(now);
            osc.stop(now + 0.15);
        }
    } catch (e) {}
}

// --- Clock & Canvas Hologram ---
function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById("clock");
    if (clockEl) clockEl.innerText = now.toTimeString().split(" ")[0];
}
setInterval(updateClock, 1000);
updateClock();

const canvas = document.getElementById("arcCanvas");
const ctx = canvas ? canvas.getContext("2d") : null;
let animAngle = 0;
let pulseVal = 0;

function drawArcReactor() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const config = PERSONA_CONFIGS[currentPersona] || PERSONA_CONFIGS.tony;
    const hexColor = config.color;

    let speed = 0.02;
    if (currentState === "THINKING") speed = 0.08;
    else if (currentState === "SPEAKING") speed = 0.05;
    else if (currentState === "LISTENING") speed = 0.04;

    animAngle += speed;
    pulseVal += 0.04;

    // Outer Glow
    const glowRad = 105 + Math.sin(pulseVal) * (currentState === "SPEAKING" ? 8 : 3);
    const grad = ctx.createRadialGradient(centerX, centerY, 20, centerX, centerY, glowRad);
    grad.addColorStop(0, hexColor + "88");
    grad.addColorStop(0.5, hexColor + "33");
    grad.addColorStop(1, "transparent");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(centerX, centerY, glowRad, 0, Math.PI * 2);
    ctx.fill();

    // Outer Ring
    ctx.strokeStyle = hexColor;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, 95, 0, Math.PI * 2);
    ctx.stroke();

    // Rotating Segments
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(animAngle);
    const segments = currentPersona === "ultron" ? 6 : 8;
    for (let i = 0; i < segments; i++) {
        const theta = (i * Math.PI * 2) / segments;
        ctx.strokeStyle = hexColor;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(0, 0, 75, theta, theta + 0.35);
        ctx.stroke();
    }
    ctx.restore();

    // Core Pulse
    const coreRadius = 22 + Math.sin(pulseVal * 2) * (currentState === "SPEAKING" ? 5 : 2);
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

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        populateVoiceSelects(window.speechSynthesis.getVoices());
    };
}

window.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    switchPersona('tony');
});
