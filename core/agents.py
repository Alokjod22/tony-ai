import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional

class SubAgentRole:
    SENTINEL = "sentinel"      # Security, integrity & vulnerability scanning
    SYNTHESIZER = "synthesizer"# Multi-source web search & deep factual research
    ARCHITECT = "architect"    # Code construction, refactoring & test generation
    COMMANDER = "commander"    # OS actions, ADB shell commands, automation
    ANALYST = "analyst"        # Data processing, math & telemetry optimization

AGENT_PROFILES = {
    SubAgentRole.SENTINEL: {
        "name": "SENTINEL-1",
        "icon": "🛡️",
        "title": "Tactical Security & Health Auditor",
        "prompt": "You are SENTINEL-1, specialized in system security, memory leak detection, port analysis, and safety auditing. Give a crisp, structured threat & diagnostic report."
    },
    SubAgentRole.SYNTHESIZER: {
        "name": "SYNTHESIZER-9",
        "icon": "⚡",
        "title": "Deep Knowledge & Web Synthesizer",
        "prompt": "You are SYNTHESIZER-9, specialized in multi-source intelligence gathering, academic analysis, and technological trend distillation. Provide dense, factual findings."
    },
    SubAgentRole.ARCHITECT: {
        "name": "ARCHITECT-X",
        "icon": "🛠️",
        "title": "Autonomous Software Engineer",
        "prompt": "You are ARCHITECT-X, a master software architect and bug triager. Write modular, robust, production-grade code and provide actionable implementation steps."
    },
    SubAgentRole.COMMANDER: {
        "name": "COMMANDER-V",
        "icon": "📱",
        "title": "Device & System Operations Commander",
        "prompt": "You are COMMANDER-V, specialized in OS-level automation, ADB Android control, and hardware coordination. Detail precise operational steps."
    },
    SubAgentRole.ANALYST: {
        "name": "ANALYST-4",
        "icon": "📊",
        "title": "Computational & Telemetry Analyst",
        "prompt": "You are ANALYST-4, specialized in quantitative modeling, system bottleneck profiling, and algorithmic calculations. Give numerical and logical solutions."
    }
}

class AgentSwarmEngine:
    """Orchestrates autonomous multi-agent swarms with concurrent execution and unified synthesis."""

    def __init__(self, brain_ref: Any = None):
        self.brain = brain_ref

    def set_brain(self, brain_ref: Any):
        self.brain = brain_ref

    def _execute_single_agent(self, role: str, task_objective: str) -> Dict[str, Any]:
        profile = AGENT_PROFILES.get(role, AGENT_PROFILES[SubAgentRole.SYNTHESIZER])
        agent_time = time.time()

        prompt = f"""{profile['prompt']}

MISSION OBJECTIVE:
"{task_objective}"

Provide your specialized agent perspective, actionable findings, and recommendations for this mission. Be direct, authoritative, and tactical (max 3 concise paragraphs)."""

        if self.brain and hasattr(self.brain, "generate_raw_text"):
            try:
                response_text = self.brain.generate_raw_text(prompt)
            except Exception as e:
                response_text = f"Agent communication failure: {str(e)}"
        else:
            response_text = f"Simulated report from {profile['name']}: Objective '{task_objective}' analyzed successfully."

        elapsed_agent = round((time.time() - agent_time) * 1000, 1)

        return {
            "role": role,
            "name": profile["name"],
            "icon": profile["icon"],
            "title": profile["title"],
            "report": response_text,
            "latency_ms": elapsed_agent,
            "status": "COMPLETED"
        }

    def dispatch_swarm(self, task_objective: str, agent_roles: Optional[List[str]] = None) -> Dict[str, Any]:
        """Dispatches a synchronized swarm of specialized agents to tackle a complex objective in parallel."""
        if not agent_roles:
            agent_roles = [
                SubAgentRole.ARCHITECT,
                SubAgentRole.SENTINEL,
                SubAgentRole.SYNTHESIZER
            ]

        start_time = time.time()

        # Concurrent execution across subagents for ultra-fast response
        with ThreadPoolExecutor(max_workers=min(len(agent_roles), 5)) as executor:
            futures = [executor.submit(self._execute_single_agent, role, task_objective) for role in agent_roles]
            agent_reports = [f.result() for f in futures]

        total_latency = round((time.time() - start_time) * 1000, 1)

        # Generate Master Unified Synthesis
        synthesis_prompt = f"""You are TONY AI — TACTICAL COMMANDER.
Synthesize the following reports from your autonomous subagents into a unified master tactical brief:

OBJECTIVE: {task_objective}

SUBAGENT REPORTS:
"""
        for r in agent_reports:
            synthesis_prompt += f"\n--- [{r['name']} ({r['title']})] ---\n{r['report']}\n"

        synthesis_prompt += "\nOutput a crisp, commanding Master Tactical Summary with clear next actions."

        if self.brain and hasattr(self.brain, "generate_raw_text"):
            try:
                master_synthesis = self.brain.generate_raw_text(synthesis_prompt)
            except Exception as e:
                master_synthesis = f"Synthesis compilation error: {str(e)}"
        else:
            master_synthesis = f"Master briefing: Swarm analyzed '{task_objective}' across {len(agent_reports)} vectors."

        return {
            "objective": task_objective,
            "swarm_size": len(agent_reports),
            "agents": agent_reports,
            "master_synthesis": master_synthesis,
            "total_latency_ms": total_latency,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
