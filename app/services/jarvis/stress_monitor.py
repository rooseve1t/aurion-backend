"""
🧠 StressMonitor — Мониторинг стресса и выгорания пользователя
Вдохновлён Iron Man 2: JARVIS мониторит уровень палладия в крови Тони непрерывно.
Наш аналог: мониторинг паттернов взаимодействия для обнаружения стресса/выгорания.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis-stress-monitor")

POLL_INTERVAL_SEC = 600        # Каждые 10 минут
ALERT_THRESHOLD = 0.70         # 70% — порог оповещения
COOLDOWN_SEC = 3600            # Не чаще 1 раза в час
MIN_MESSAGES_FOR_ANALYSIS = 3  # Минимум сообщений для анализа


@dataclass
class StressIndicators:
    messages_last_hour: int
    rapid_fire_count: int          # Сообщения < 15с друг от друга
    avg_message_length: float
    late_night_activity: bool      # После 23:00
    error_keyword_count: int       # "ошибка", "не работает", "сломалось" и т.д.
    session_duration_minutes: float
    score: float                   # 0.0-1.0
    level: str                     # "normal" | "elevated" | "high" | "critical"


ERROR_KEYWORDS = [
    "ошибка", "не работает", "сломал", "проблема", "баг", "сбой",
    "не могу", "почему", "опять", "снова", "достал", "надоел",
    "error", "broken", "problem", "bug", "crash", "fail"
]


class StressMonitor:
    """Мониторит стресс пользователя через паттерны взаимодействия"""

    def __init__(self) -> None:
        self._monitoring_users: Dict[str, bool] = {}

    async def analyze_session(
        self,
        user_id: str,
        db: Any,
    ) -> Optional[StressIndicators]:
        """
        Анализирует сессию пользователя за последний час.
        Возвращает StressIndicators или None если данных недостаточно.
        """
        try:
            from sqlalchemy import select, and_
            from ...models.memory import MemoryEntry

            cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
            user_id_col = getattr(MemoryEntry, "user_id")
            created_at_col = getattr(MemoryEntry, "created_at")
            content_col = getattr(MemoryEntry, "content")

            stmt = (
                select(MemoryEntry)
                .where(and_(user_id_col == user_id, created_at_col >= cutoff))
                .order_by(created_at_col.asc())
            )
            result = await db.execute(stmt)
            entries = list(result.scalars().all())

            if len(entries) < MIN_MESSAGES_FOR_ANALYSIS:
                return None

            # Анализируем
            messages_count = len(entries)
            rapid_fire = 0
            error_kw_count = 0
            lengths = []

            timestamps = []
            for entry in entries:
                ts = getattr(entry, "created_at")
                if ts and ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts:
                    timestamps.append(ts)

                # Декодируем контент
                import base64
                raw = getattr(entry, "content", "") or ""
                try:
                    text = base64.b64decode(raw[4:]).decode() if raw.startswith("PQV_") else raw
                except Exception:
                    text = raw
                lengths.append(len(text))

                # Ключевые слова стресса
                text_lower = text.lower()
                for kw in ERROR_KEYWORDS:
                    if kw in text_lower:
                        error_kw_count += 1
                        break

            # Rapid-fire: сообщения с интервалом < 15 секунд
            for i in range(1, len(timestamps)):
                delta = (timestamps[i] - timestamps[i-1]).total_seconds()
                if 0 < delta < 15:
                    rapid_fire += 1

            # Ночная активность
            current_hour = datetime.now(timezone.utc).hour
            late_night = current_hour >= 23 or current_hour <= 4

            # Длительность сессии (от первого до последнего сообщения)
            if len(timestamps) >= 2:
                session_min = (timestamps[-1] - timestamps[0]).total_seconds() / 60
            else:
                session_min = 0.0

            avg_length = sum(lengths) / len(lengths) if lengths else 0

            # Вычисляем стресс-скор
            score = self._compute_score(
                messages_count, rapid_fire, late_night, error_kw_count, session_min
            )

            level = self._score_to_level(score)

            return StressIndicators(
                messages_last_hour=messages_count,
                rapid_fire_count=rapid_fire,
                avg_message_length=avg_length,
                late_night_activity=late_night,
                error_keyword_count=error_kw_count,
                session_duration_minutes=session_min,
                score=score,
                level=level,
            )

        except Exception as exc:
            logger.warning(f"StressMonitor.analyze_session error: {exc}")
            return None

    def _compute_score(
        self,
        messages: int,
        rapid_fire: int,
        late_night: bool,
        error_kw: int,
        session_min: float,
    ) -> float:
        """Взвешенная формула стресс-скора"""
        # Нормализуем каждый фактор к [0, 1]
        msg_factor = min(messages / 30, 1.0)         # 30+ сообщений/час = макс
        rapid_factor = min(rapid_fire / 10, 1.0)     # 10+ быстрых = макс
        night_factor = 1.0 if late_night else 0.0
        error_factor = min(error_kw / 5, 1.0)        # 5+ слов стресса = макс
        session_factor = min(session_min / 120, 1.0) # 2+ часа = макс

        score = (
            msg_factor * 0.25 +
            rapid_factor * 0.25 +
            night_factor * 0.20 +
            error_factor * 0.20 +
            session_factor * 0.10
        )
        return min(score, 1.0)

    def _score_to_level(self, score: float) -> str:
        if score < 0.40:
            return "normal"
        elif score < 0.60:
            return "elevated"
        elif score < ALERT_THRESHOLD:
            return "high"
        else:
            return "critical"

    async def check_and_alert(
        self,
        user_id: str,
        indicators: StressIndicators,
        redis_client: Any,
    ) -> bool:
        """Отправляет оповещение если стресс превышает порог и нет cooldown"""
        if indicators.score < ALERT_THRESHOLD:
            return False

        if redis_client is None:
            return False

        cooldown_key = f"stress_alert:{user_id}"
        try:
            existing = await redis_client.get(cooldown_key)
            if existing:
                return False  # В cooldown

            # Публикуем событие
            event = {
                "type": "stress_alert",
                "domain": "health",
                "priority": "high",
                "stress_level": indicators.level,
                "stress_score": round(indicators.score * 100),
                "message": self._format_alert_message(indicators),
                "indicators": {
                    "messages_last_hour": indicators.messages_last_hour,
                    "rapid_fire_count": indicators.rapid_fire_count,
                    "late_night": indicators.late_night_activity,
                    "error_keywords": indicators.error_keyword_count,
                    "session_minutes": round(indicators.session_duration_minutes),
                },
            }
            channel = f"jarvis:events:{user_id}"
            await redis_client.publish(channel, json.dumps(event))

            # Устанавливаем cooldown
            await redis_client.setex(cooldown_key, COOLDOWN_SEC, "1")
            logger.info(f"Stress alert sent for user {user_id}: score={indicators.score:.2f}")
            return True

        except Exception as exc:
            logger.warning(f"Stress alert error: {exc}")
            return False

    def _format_alert_message(self, indicators: StressIndicators) -> str:
        """JARVIS-стиль сообщения о стрессе (как мониторинг палладия в Iron Man 2)"""
        score_pct = round(indicators.score * 100)
        msgs = []

        if indicators.late_night_activity:
            msgs.append("поздняя ночная сессия")
        if indicators.rapid_fire_count > 5:
            msgs.append(f"{indicators.rapid_fire_count} быстрых сообщений подряд")
        if indicators.error_keyword_count > 2:
            msgs.append("признаки фрустрации в тексте")
        if indicators.session_duration_minutes > 90:
            msgs.append(f"сессия {round(indicators.session_duration_minutes)} минут")

        context = ", ".join(msgs) if msgs else "интенсивная активность"

        return (
            f"Сэр, индекс стресса достиг {score_pct}%. "
            f"Детектировано: {context}. "
            f"Рекомендую сделать перерыв."
        )

    def get_stress_index(self, indicators: Optional[StressIndicators]) -> int:
        """Возвращает стресс-индекс 0-100 для HUD"""
        if indicators is None:
            return 0
        return round(indicators.score * 100)


# Синглтон
_instance: Optional[StressMonitor] = None


def get_stress_monitor() -> StressMonitor:
    global _instance
    if _instance is None:
        _instance = StressMonitor()
    return _instance
