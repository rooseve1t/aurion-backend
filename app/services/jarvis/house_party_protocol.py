"""
House Party Protocol — JARVIS Iron Man 3
"JARVIS, it's time for a little House Party Protocol"
Deploys all 8 squad agents simultaneously to achieve a single goal.
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis-house-party")

AGENT_ROLES = [
    ("cto", "Alpha — CTO", "Strategic architecture and technical leadership"),
    ("tech_lead", "Sigma — Tech Lead", "Task decomposition and technical planning"),
    ("senior_dev", "Lux — Senior Developer", "Implementation of key components"),
    ("qa", "Omega — QA Engineer", "Testing and quality assurance"),
    ("security", "Sentinel — Security", "Security analysis and protection"),
    ("devops", "Flux — DevOps", "Infrastructure and deployment"),
    ("analyst", "Nexus — Analyst", "Prioritization and analytics"),
    ("researcher", "Echo — Researcher", "Research and innovation"),
]

ROLE_SYSTEM_PROMPTS = {
    "cto": "You are a CTO. Give a strategic assessment of the task: architectural decisions, tech stack, risks.",
    "tech_lead": "You are a Tech Lead. Decompose the task into concrete technical steps with time estimates.",
    "senior_dev": "You are a Senior Developer. Describe the concrete implementation: patterns, code, data structures.",
    "qa": "You are a QA Engineer. Describe the testing strategy: unit tests, integration tests, edge cases.",
    "security": "You are a Security specialist. Analyze threats, vulnerabilities and protective measures.",
    "devops": "You are a DevOps Engineer. Describe infrastructure, CI/CD, monitoring and deployment.",
    "analyst": "You are an Analyst. Evaluate priorities, success metrics, potential problems.",
    "researcher": "You are a Researcher. Find analogues, best practices, innovative approaches.",
}


@dataclass
class AgentDeployStatus:
    role: str
    name: str
    description: str
    status: str = "idle"       # idle | deploying | working | complete | failed
    output: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class HousePartySession:
    session_id: str
    user_id: str
    goal: str
    status: str = "deploying"  # deploying | complete | failed
    agent_statuses: Dict[str, AgentDeployStatus] = field(default_factory=dict)
    final_report: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


# In-memory session store (sufficient for MVP)
_sessions: Dict[str, HousePartySession] = {}


class HousePartyProtocol:
    """
    Protocol for simultaneous deployment of all agents.
    Iron Man 3: JARVIS controls 35 suits in parallel.
    """

    def __init__(self) -> None:
        self.llm_client: Any = None

    def _get_llm_client(self) -> Any:
        """Lazy init OpenAI client"""
        if self.llm_client is None:
            import os
            try:
                from openai import AsyncOpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.llm_client = AsyncOpenAI(api_key=api_key)
            except Exception as e:
                logger.warning(f"OpenAI client init failed: {e}")
        return self.llm_client

    async def activate(
        self,
        user_id: str,
        goal: str,
        redis_client: Any = None,
    ) -> str:
        """
        Activates House Party Protocol.
        Returns session_id for tracking progress.
        """
        session_id = str(uuid.uuid4())[:8]

        session = HousePartySession(
            session_id=session_id,
            user_id=user_id,
            goal=goal,
        )

        # Initialize statuses for all agents
        for role_id, name, description in AGENT_ROLES:
            session.agent_statuses[role_id] = AgentDeployStatus(
                role=role_id,
                name=name,
                description=description,
                status="idle",
            )

        _sessions[session_id] = session

        logger.info(f"House Party Protocol ACTIVATED | session={session_id} | goal: {goal[:50]}...")

        # Publish start event
        await self._publish_event(user_id, redis_client, {
            "type": "house_party_started",
            "session_id": session_id,
            "goal": goal,
            "agents": [asdict(s) for s in session.agent_statuses.values()],
        })

        # Launch all agents in parallel as a background task
        asyncio.create_task(
            self._deploy_all_agents(session_id, user_id, goal, redis_client)
        )

        return session_id

    async def _deploy_all_agents(
        self,
        session_id: str,
        user_id: str,
        goal: str,
        redis_client: Any,
    ) -> None:
        """Launches all agents in parallel via asyncio.gather"""
        session = _sessions.get(session_id)
        if not session:
            return

        tasks = [
            self._run_agent_task(session_id, user_id, role_id, name, goal, redis_client)
            for role_id, name, _ in AGENT_ROLES
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Synthesize final report
        outputs: Dict[str, str] = {}
        for i, (role_id, name, _) in enumerate(AGENT_ROLES):
            result = results[i]
            if isinstance(result, Exception):
                outputs[role_id] = f"Error: {result}"
            else:
                outputs[role_id] = str(result)

        final_report = await self._synthesize_report(goal, outputs)

        session.status = "complete"
        session.final_report = final_report
        session.completed_at = datetime.now(timezone.utc).isoformat()

        await self._publish_event(user_id, redis_client, {
            "type": "house_party_complete",
            "session_id": session_id,
            "final_report": final_report,
            "status": "complete",
        })

        logger.info(f"House Party Protocol COMPLETE | session={session_id}")

    async def _run_agent_task(
        self,
        session_id: str,
        user_id: str,
        role_id: str,
        name: str,
        goal: str,
        redis_client: Any,
    ) -> str:
        """Runs a single agent and publishes progress events"""
        session = _sessions.get(session_id)
        if not session or role_id not in session.agent_statuses:
            return ""

        agent_status = session.agent_statuses[role_id]
        agent_status.status = "working"
        agent_status.started_at = datetime.now(timezone.utc).isoformat()

        # Publish "working" status
        await self._publish_event(user_id, redis_client, {
            "type": "house_party_agent_update",
            "session_id": session_id,
            "role": role_id,
            "status": "working",
            "name": name,
        })

        try:
            output = await self._call_llm_for_role(role_id, goal)
            agent_status.status = "complete"
            agent_status.output = output
            agent_status.completed_at = datetime.now(timezone.utc).isoformat()

            await self._publish_event(user_id, redis_client, {
                "type": "house_party_agent_update",
                "session_id": session_id,
                "role": role_id,
                "status": "complete",
                "name": name,
                "output": output[:500],  # Limit for WebSocket payload
            })

            return output

        except Exception as e:
            logger.error(f"Agent {role_id} failed: {e}")
            agent_status.status = "failed"
            agent_status.output = f"Execution error: {e}"
            agent_status.completed_at = datetime.now(timezone.utc).isoformat()

            await self._publish_event(user_id, redis_client, {
                "type": "house_party_agent_update",
                "session_id": session_id,
                "role": role_id,
                "status": "failed",
                "name": name,
                "output": str(e),
            })

            return f"Error: {e}"

    async def _call_llm_for_role(self, role_id: str, goal: str) -> str:
        """Calls the LLM with the system prompt for the given role"""
        system_prompt = ROLE_SYSTEM_PROMPTS.get(role_id, "You are an assistant. Help with the task.")
        client = self._get_llm_client()

        if client is None:
            # Fallback without LLM
            await asyncio.sleep(1)
            return f"[Simulation] Analysis of task '{goal[:50]}' complete. LLM unavailable."

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Task: {goal}\n\nProvide a concrete analysis in 3-5 sentences."},
                ],
                max_tokens=400,
                temperature=0.7,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.warning(f"LLM call failed for {role_id}: {e}")
            return f"[LLM Error] {e}"

    async def _synthesize_report(self, goal: str, outputs: Dict[str, str]) -> str:
        """Synthesizes the final report from all agent responses"""
        client = self._get_llm_client()

        sections = []
        for role_id, name, _ in AGENT_ROLES:
            output = outputs.get(role_id, "")
            if output:
                sections.append(f"**{name}**: {output}")

        combined = "\n\n".join(sections)

        if client is None:
            return f"# House Party Protocol Report\n\n**Goal**: {goal}\n\n{combined}"

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are JARVIS. Synthesize a concise executive report from the team's analysis."
                    },
                    {
                        "role": "user",
                        "content": f"Goal: {goal}\n\nTeam analysis:\n{combined}\n\nProvide a summary report in 5-7 sentences."
                    },
                ],
                max_tokens=600,
                temperature=0.5,
            )
            synthesis = response.choices[0].message.content or combined
            return (
                f"# House Party Protocol — Final Report\n\n"
                f"**Goal**: {goal}\n\n"
                f"## JARVIS Synthesis\n{synthesis}\n\n"
                f"## Agent Details\n{combined}"
            )
        except Exception as e:
            logger.warning(f"Report synthesis failed: {e}")
            return f"# House Party Protocol Report\n\n**Goal**: {goal}\n\n{combined}"

    async def _publish_event(self, user_id: str, redis_client: Any, event: Dict[str, Any]) -> None:
        """Publishes an event to Redis pub/sub"""
        if redis_client is None:
            return
        try:
            channel = f"jarvis:events:{user_id}"
            await redis_client.publish(channel, json.dumps(event))
        except Exception as e:
            logger.warning(f"Failed to publish house party event: {e}")

    def get_session(self, session_id: str) -> Optional[HousePartySession]:
        return _sessions.get(session_id)

    def list_sessions(self, user_id: str) -> List[HousePartySession]:
        return [s for s in _sessions.values() if s.user_id == user_id]


# Singleton
_instance: Optional[HousePartyProtocol] = None


def get_house_party_protocol() -> HousePartyProtocol:
    global _instance
    if _instance is None:
        _instance = HousePartyProtocol()
    return _instance
