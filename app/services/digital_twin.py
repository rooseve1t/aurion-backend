"""
DigitalTwinService — цифровой двойник здоровья пользователя.

Три уровня:
  1. Живая панель (get_live_metrics)    — текущие показатели из Redis/БД
  2. Анализ паттернов (get_patterns)    — агрегация за week/month/quarter
  3. Рекомендации (get_recommendations) — LLM-анализ паттернов
"""
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

logger = logging.getLogger("aurion-digital-twin")


@dataclass
class HealthMetrics:
    heart_rate: Optional[int] = None
    steps: Optional[int] = None
    sleep_hours: Optional[float] = None
    activity_minutes: Optional[int] = None
    source: str = "manual"
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class HealthPattern:
    metric: str
    period: str       # week | month | quarter
    trend: str        # improving | stable | declining
    data_points: list = field(default_factory=list)


class DigitalTwinService:

    def __init__(self) -> None:
        self._redis: Any = None

    def set_redis(self, client: Any) -> None:
        self._redis = client

    # ------------------------------------------------------------------
    # Уровень 1: живые показатели
    # ------------------------------------------------------------------

    async def get_live_metrics(self, user_id: str) -> Optional[HealthMetrics]:
        if self._redis:
            try:
                import json
                raw = await self._redis.get(f"health:live:{user_id}")
                if raw:
                    data = json.loads(raw.decode() if isinstance(raw, bytes) else raw)
                    valid = {k: v for k, v in data.items() if k in HealthMetrics.__dataclass_fields__}
                    return HealthMetrics(**valid)
            except Exception as exc:
                logger.warning(f"DigitalTwin: Redis live metrics failed: {exc}")
        return await self._get_latest_from_db(user_id)

    async def _get_latest_from_db(self, user_id: str) -> Optional[HealthMetrics]:
        try:
            from ..database_final import AsyncSessionLocal
            from sqlalchemy import select, desc, text

            async with AsyncSessionLocal() as db:
                # Используем raw query для совместимости — модель HealthRecord может отсутствовать
                result = await db.execute(
                    text(
                        "SELECT heart_rate, steps, sleep_hours, activity_minutes, source, recorded_at "
                        "FROM health_records WHERE user_id = :uid ORDER BY recorded_at DESC LIMIT 1"
                    ),
                    {"uid": str(user_id)},
                )
                row = result.fetchone()
                if row:
                    return HealthMetrics(
                        heart_rate=row[0],
                        steps=row[1],
                        sleep_hours=row[2],
                        activity_minutes=row[3],
                        source=row[4] or "db",
                        recorded_at=row[5].isoformat() if hasattr(row[5], "isoformat") else str(row[5]),
                    )
        except Exception as exc:
            logger.warning(f"DigitalTwin: DB live metrics failed: {exc}")
        return None

    # ------------------------------------------------------------------
    # Уровень 2: паттерны
    # ------------------------------------------------------------------

    async def get_patterns(self, user_id: str, period: str = "week") -> list[HealthPattern]:
        period_days = {"week": 7, "month": 30, "quarter": 90}.get(period, 7)
        since = datetime.now(timezone.utc) - timedelta(days=period_days)
        records = await self._get_records_since(user_id, since)
        if not records:
            return []

        patterns: list[HealthPattern] = []
        for metric in ("heart_rate", "steps", "sleep_hours", "activity_minutes"):
            values = [r.get(metric) for r in records if r.get(metric) is not None]
            if len(values) < 2:
                continue
            patterns.append(HealthPattern(
                metric=metric,
                period=period,
                trend=self._calc_trend(values),
                data_points=values[-30:],
            ))
        return patterns

    def _calc_trend(self, values: list) -> str:
        if len(values) < 2:
            return "stable"
        mid = len(values) // 2
        first = sum(values[:mid]) / mid
        second = sum(values[mid:]) / (len(values) - mid)
        delta = (second - first) / (first + 1e-9)
        if delta > 0.05:
            return "improving"
        if delta < -0.05:
            return "declining"
        return "stable"

    async def _get_records_since(self, user_id: str, since: datetime) -> list[dict]:
        try:
            from ..database_final import AsyncSessionLocal
            from sqlalchemy import text

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    text(
                        "SELECT heart_rate, steps, sleep_hours, activity_minutes "
                        "FROM health_records WHERE user_id = :uid AND recorded_at >= :since "
                        "ORDER BY recorded_at"
                    ),
                    {"uid": str(user_id), "since": since},
                )
                return [
                    {"heart_rate": r[0], "steps": r[1], "sleep_hours": r[2], "activity_minutes": r[3]}
                    for r in result.fetchall()
                ]
        except Exception as exc:
            logger.warning(f"DigitalTwin: get_records_since failed: {exc}")
            return []

    # ------------------------------------------------------------------
    # Уровень 3: рекомендации
    # ------------------------------------------------------------------

    async def get_recommendations(self, user_id: str) -> list[dict]:
        patterns = await self.get_patterns(user_id, "month")
        if not patterns:
            return [{"text": "Недостаточно данных для анализа. Добавьте показатели здоровья."}]

        summary = "; ".join(f"{p.metric}: тренд {p.trend} за {p.period}" for p in patterns)

        try:
            from .voice_jarvis_service import get_jarvis_service
            jarvis = get_jarvis_service()
            if jarvis:
                prompt = (
                    f"Проанализируй показатели здоровья: {summary}. "
                    "Дай 3 конкретные рекомендации на русском языке, кратко."
                )
                response = await jarvis.generate_response(prompt)
                return [{"text": response}]
        except Exception as exc:
            logger.warning(f"DigitalTwin: LLM recommendations failed: {exc}")

        recs = [
            {"text": f"Показатель «{p.metric}» ухудшается. Обратите внимание."}
            for p in patterns if p.trend == "declining"
        ]
        return recs or [{"text": "Показатели здоровья в норме. Продолжайте в том же духе."}]

    # ------------------------------------------------------------------
    # Ручной ввод
    # ------------------------------------------------------------------

    async def ingest_manual(self, user_id: str, metrics: HealthMetrics) -> None:
        if self._redis:
            try:
                import json
                await self._redis.setex(
                    f"health:live:{user_id}", 3600, json.dumps(asdict(metrics))
                )
            except Exception as exc:
                logger.warning(f"DigitalTwin: Redis cache update failed: {exc}")

        try:
            from ..database_final import AsyncSessionLocal
            from sqlalchemy import text

            async with AsyncSessionLocal() as db:
                await db.execute(
                    text(
                        "INSERT INTO health_records "
                        "(user_id, heart_rate, steps, sleep_hours, activity_minutes, source) "
                        "VALUES (:uid, :hr, :steps, :sleep, :activity, :source)"
                    ),
                    {
                        "uid": str(user_id),
                        "hr": metrics.heart_rate,
                        "steps": metrics.steps,
                        "sleep": metrics.sleep_hours,
                        "activity": metrics.activity_minutes,
                        "source": metrics.source,
                    },
                )
                await db.commit()
        except Exception as exc:
            logger.warning(f"DigitalTwin: ingest_manual DB save failed: {exc}")


_twin: Optional[DigitalTwinService] = None


def get_digital_twin() -> DigitalTwinService:
    global _twin
    if _twin is None:
        _twin = DigitalTwinService()
    return _twin
