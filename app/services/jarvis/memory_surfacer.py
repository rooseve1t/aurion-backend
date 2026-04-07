"""
🧠 MemorySurfacer — Проактивное всплытие воспоминаний JARVIS
Аналог того, как JARVIS в фильмах помнит разговоры неделями и упоминает их естественно.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.memory import MemoryEntry
from ..memory_service import MemoryService, _encode_text, _cosine_similarity

logger = logging.getLogger("jarvis-memory-surfacer")

CONFIDENCE_THRESHOLD = 0.60
MAX_SURFACE_PER_RESPONSE = 1
MIN_MEMORY_AGE_DAYS = 3


@dataclass
class SurfacedMemory:
    id: str
    title: str
    content_preview: str
    created_at: datetime
    match_score: float
    days_ago: int


class MemorySurfacer:
    """
    Просматривает старые воспоминания и всплывает релевантные в разговоре.
    Реализует поведение JARVIS из всех фильмов Iron Man — он ВСЕГДА помнит прошлое.
    """

    def __init__(self) -> None:
        pass

    async def find_relevant_memory(
        self,
        user_id: str,
        current_message: str,
        db: AsyncSession,
    ) -> Optional[SurfacedMemory]:
        """
        Ищет воспоминания старше MIN_MEMORY_AGE_DAYS дней, семантически близкие к текущему сообщению.
        Возвращает наиболее релевантное воспоминание или None.
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=MIN_MEMORY_AGE_DAYS)
            user_id_col = getattr(MemoryEntry, "user_id")
            created_at_col = getattr(MemoryEntry, "created_at")

            stmt = (
                select(MemoryEntry)
                .where(
                    and_(
                        user_id_col == user_id,
                        created_at_col < cutoff_date,
                    )
                )
                .order_by(created_at_col.desc())
                .limit(50)
            )
            result = await db.execute(stmt)
            candidates: List[MemoryEntry] = list(result.scalars().all())

            if not candidates:
                return None

            query_embedding = _encode_text(current_message)
            best_match: Optional[SurfacedMemory] = None
            best_score = 0.0

            for entry in candidates:
                embedding = getattr(entry, "embedding", None)
                if not embedding:
                    continue
                score = _cosine_similarity(query_embedding, embedding)
                if score > best_score and score >= CONFIDENCE_THRESHOLD:
                    best_score = score
                    created = getattr(entry, "created_at")
                    if created and created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                    days_ago = (datetime.now(timezone.utc) - created).days if created else 0
                    content_raw = getattr(entry, "content", "") or ""
                    # Decrypt mock: content starts with "PQV_"
                    import base64
                    try:
                        if content_raw.startswith("PQV_"):
                            content_preview = base64.b64decode(content_raw[4:]).decode("utf-8")[:150]
                        else:
                            content_preview = content_raw[:150]
                    except Exception:
                        content_preview = content_raw[:150]

                    best_match = SurfacedMemory(
                        id=str(getattr(entry, "id")),
                        title=getattr(entry, "title", None) or "Воспоминание",
                        content_preview=content_preview,
                        created_at=created or datetime.now(timezone.utc),
                        match_score=score,
                        days_ago=days_ago,
                    )

            return best_match

        except Exception as exc:
            logger.warning(f"MemorySurfacer.find_relevant_memory error: {exc}")
            return None

    def format_surfacing_phrase(self, memory: SurfacedMemory) -> str:
        """
        Генерирует фразу в стиле JARVIS для всплытия воспоминания.
        Примеры из фильмов: "По поводу вашего вопроса о реакторе прошлой недели..."
        """
        days_ago = memory.days_ago

        if days_ago == 1:
            time_ref = "вчера"
        elif days_ago <= 6:
            time_ref = f"{days_ago} дня назад"
        elif days_ago <= 13:
            time_ref = "на прошлой неделе"
        elif days_ago <= 30:
            weeks = days_ago // 7
            time_ref = f"{weeks} {'неделю' if weeks == 1 else 'недели'} назад"
        else:
            time_ref = f"{days_ago // 30} месяц{'а' if days_ago // 30 < 5 else 'ев'} назад"

        phrases = [
            f"\n\n_Кстати, сэр — {time_ref} вы касались темы «{memory.title}». Возможно, это релевантно._",
            f"\n\n_По этому поводу: {time_ref} в базе зафиксировано: «{memory.content_preview[:80]}...»_",
            f"\n\n_Позвольте отметить, сэр: {time_ref} мы уже обсуждали смежную тему — «{memory.title}»._",
        ]

        import hashlib
        idx = int(hashlib.md5(memory.id.encode()).hexdigest(), 16) % len(phrases)
        return phrases[idx]


# Синглтон
_instance: Optional[MemorySurfacer] = None


def get_memory_surfacer() -> MemorySurfacer:
    global _instance
    if _instance is None:
        _instance = MemorySurfacer()
    return _instance
