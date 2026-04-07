"""
PassiveResearcher - Passive background researcher for JARVIS
Inspired by the Avengers scene: while Tony talks to the team, JARVIS silently
hacks SHIELD's entire database and gathers intelligence.
Our analog: JARVIS silently researches topics from conversations and accumulates knowledge.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis-passive-researcher")

RESEARCH_INTERVAL_SEC = 3600    # Every hour
MAX_TOPICS_PER_CYCLE = 3        # No more than 3 topics per cycle (LLM economy)
MIN_CONV_AGE_HOURS = 1          # Conversation must "settle"
MAX_CONV_AGE_HOURS = 48         # Don't analyze too old conversations
RESEARCH_IMPORTANCE = 8         # High importance for auto-research
RESEARCH_TTL_DAYS = 7           # Don't repeat topic for 7 days


@dataclass
class ResearchTopic:
    name: str
    keywords: List[str]
    hash: str  # SHA256[:16] for deduplication


@dataclass
class ResearchResult:
    topic: ResearchTopic
    summary: str
    key_points: List[str]


class PassiveResearcher:
    """
    Background researcher - works silently, like JARVIS in the Avengers.
    Results are saved in MemoryEntry and available via MemorySurfacer.
    """

    def __init__(self) -> None:
        self._running = False
        self._llm_client: Any = None

    def _get_llm_client(self) -> Any:
        if self._llm_client is None:
            import os
            try:
                from openai import AsyncOpenAI
                key = os.getenv("OPENAI_API_KEY")
                if key:
                    self._llm_client = AsyncOpenAI(api_key=key)
            except Exception as e:
                logger.warning(f"LLM client init failed: {e}")
        return self._llm_client

    async def run_cycle(self, user_id: str, db: Any, redis_client: Any) -> int:
        """
        Performs one passive research cycle.
        Returns number of saved insights.
        """
        try:
            topics = await self._extract_topics(user_id, db)
            if not topics:
                return 0

            saved = 0
            for topic in topics[:MAX_TOPICS_PER_CYCLE]:
                # Check deduplication
                if redis_client and await self._has_been_researched(topic.hash, user_id, redis_client):
                    logger.debug(f"Topic '{topic.name}' already researched, skipping")
                    continue

                result = await self._research_topic(topic)
                if result:
                    await self._store_insight(user_id, result, db)
                    if redis_client:
                        await self._mark_researched(topic.hash, user_id, redis_client)
                    saved += 1
                    logger.info(f"Researched: '{topic.name}' for user {user_id}")

            if saved > 0 and redis_client:
                # Notify about new insights
                event = {
                    "type": "research_insight_ready",
                    "domain": "research",
                    "priority": "low",
                    "count": saved,
                    "message": f"Background analysis complete. Added {saved} new insights to knowledge base.",
                }
                channel = f"jarvis:events:{user_id}"
                await redis_client.publish(channel, json.dumps(event))

            return saved

        except Exception as exc:
            logger.warning(f"PassiveResearcher.run_cycle error: {exc}")
            return 0

    async def _extract_topics(self, user_id: str, db: Any) -> List[ResearchTopic]:
        """Extracts topics from recent conversations via LLM"""
        try:
            from sqlalchemy import select, and_
            from ...models.memory import MemoryEntry

            min_age = datetime.now(timezone.utc) - timedelta(hours=MIN_CONV_AGE_HOURS)
            max_age = datetime.now(timezone.utc) - timedelta(hours=MAX_CONV_AGE_HOURS)

            user_id_col = getattr(MemoryEntry, "user_id")
            created_at_col = getattr(MemoryEntry, "created_at")

            stmt = (
                select(MemoryEntry)
                .where(and_(
                    user_id_col == user_id,
                    created_at_col <= min_age,
                    created_at_col >= max_age,
                ))
                .order_by(created_at_col.desc())
                .limit(20)
            )
            result = await db.execute(stmt)
            entries = list(result.scalars().all())

            if not entries:
                return []

            # Collect texts
            import base64
            texts = []
            for entry in entries:
                raw = getattr(entry, "content", "") or ""
                try:
                    text = base64.b64decode(raw[4:]).decode() if raw.startswith("PQV_") else raw
                    texts.append(text[:200])
                except Exception:
                    texts.append(raw[:200])

            combined = "\n".join(texts[:10])  # Limit

            # LLM extracts topics
            client = self._get_llm_client()
            if client is None:
                return self._extract_topics_heuristic(combined)

            try:
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Extract 1-3 unique topics from conversation fragments. "
                                "Return JSON array: [{\"name\": \"topic\", \"keywords\": [\"kw1\", \"kw2\"]}]. "
                                "JSON only, no extra text."
                            )
                        },
                        {"role": "user", "content": combined},
                    ],
                    max_tokens=200,
                    temperature=0.3,
                )
                raw_json = response.choices[0].message.content or "[]"
                # Extract JSON if wrapped
                import re
                match = re.search(r'\[.*\]', raw_json, re.DOTALL)
                if match:
                    raw_json = match.group(0)
                topics_data = json.loads(raw_json)
                topics = []
                for t in topics_data[:MAX_TOPICS_PER_CYCLE]:
                    name = t.get("name", "")
                    keywords = t.get("keywords", [])
                    if name:
                        h = hashlib.sha256(name.lower().encode()).hexdigest()[:16]
                        topics.append(ResearchTopic(name=name, keywords=keywords, hash=h))
                return topics
            except Exception as e:
                logger.warning(f"LLM topic extraction failed: {e}")
                return self._extract_topics_heuristic(combined)

        except Exception as exc:
            logger.warning(f"_extract_topics error: {exc}")
            return []

    def _extract_topics_heuristic(self, text: str) -> List[ResearchTopic]:
        """Simple heuristic without LLM"""
        import re
        words = re.findall(r'\b[a-zA-Z]{6,}\b', text)
        from collections import Counter
        freq = Counter(w.lower() for w in words)
        top = [w for w, _ in freq.most_common(5)]
        if not top:
            return []
        name = " ".join(top[:3])
        h = hashlib.sha256(name.encode()).hexdigest()[:16]
        return [ResearchTopic(name=name, keywords=top, hash=h)]

    async def _has_been_researched(self, topic_hash: str, user_id: str, redis_client: Any) -> bool:
        key = f"research:done:{user_id}:{topic_hash}"
        try:
            result = await redis_client.get(key)
            return result is not None
        except Exception:
            return False

    async def _mark_researched(self, topic_hash: str, user_id: str, redis_client: Any) -> None:
        key = f"research:done:{user_id}:{topic_hash}"
        try:
            await redis_client.setex(key, RESEARCH_TTL_DAYS * 86400, "1")
        except Exception as e:
            logger.warning(f"Failed to mark researched: {e}")

    async def _research_topic(self, topic: ResearchTopic) -> Optional[ResearchResult]:
        """Researches topic via LLM"""
        client = self._get_llm_client()
        if client is None:
            return ResearchResult(
                topic=topic,
                summary=f"[Simulation] Analysis of topic '{topic.name}'. LLM unavailable.",
                key_points=["Data unavailable without LLM"],
            )

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are JARVIS research assistant. "
                            "Give a brief, factual analysis of the topic in 2-3 paragraphs. "
                            "Focus: current state, key facts, practical significance."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Topic for research: {topic.name}\nKeywords: {', '.join(topic.keywords)}"
                    },
                ],
                max_tokens=400,
                temperature=0.4,
            )
            summary = response.choices[0].message.content or ""
            # Extract key points (first sentences of each paragraph)
            key_points = [p.split('.')[0].strip() for p in summary.split('\n\n') if p.strip()][:3]
            return ResearchResult(topic=topic, summary=summary, key_points=key_points)

        except Exception as e:
            logger.warning(f"Research LLM call failed for '{topic.name}': {e}")
            return None

    async def _store_insight(self, user_id: str, result: ResearchResult, db: Any) -> None:
        """Saves insight as a memory with high importance"""
        from ..memory_service import MemoryService

        svc = MemoryService(db)
        content = f"{result.summary}\n\nKey points: {'; '.join(result.key_points)}"
        await svc.add_memory(
            user_id=user_id,
            content=content,
            title=f"[Auto-Research] {result.topic.name}",
            tags=["auto_research", result.topic.name] + result.topic.keywords[:2],
            categories=["research"],
            importance=RESEARCH_IMPORTANCE,
            entry_metadata={
                "source": "passive_researcher",
                "topic_hash": result.topic.hash,
                "researched_at": datetime.now(timezone.utc).isoformat(),
            },
        )


# Singleton
_instance: Optional[PassiveResearcher] = None


def get_passive_researcher() -> PassiveResearcher:
    global _instance
    if _instance is None:
        _instance = PassiveResearcher()
    return _instance
