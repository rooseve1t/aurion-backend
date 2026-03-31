"""
DigitalTwin API — роутер /api/v2/health/

GET  /metrics              — живые показатели (Standard+)
GET  /patterns?period=week — паттерны (Standard+)
GET  /recommendations      — рекомендации JARVIS (Standard+)
POST /metrics              — ручной ввод данных (все уровни)
"""
import logging
from dataclasses import asdict
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ..api.auth import get_current_user
from ..middleware.subscription_guard import require_subscription, SubscriptionLevel
from ..models.user import User
from ..services.digital_twin import get_digital_twin, HealthMetrics

logger = logging.getLogger("aurion-digital-twin-api")

router = APIRouter(tags=["health-v2"])


class ManualMetricsRequest(BaseModel):
    heart_rate: Optional[int] = None
    steps: Optional[int] = None
    sleep_hours: Optional[float] = None
    activity_minutes: Optional[int] = None


@router.get("/metrics")
async def get_live_metrics(
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_subscription(SubscriptionLevel.STANDARD)),
) -> Dict[str, Any]:
    twin = get_digital_twin()
    metrics = await twin.get_live_metrics(str(current_user.id))
    if metrics is None:
        return {"data": None, "message": "Нет данных. Добавьте показатели вручную."}
    return {"data": asdict(metrics)}


@router.get("/patterns")
async def get_patterns(
    period: str = Query(default="week", pattern="^(week|month|quarter)$"),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_subscription(SubscriptionLevel.STANDARD)),
) -> Dict[str, Any]:
    twin = get_digital_twin()
    patterns = await twin.get_patterns(str(current_user.id), period)
    return {"period": period, "patterns": [asdict(p) for p in patterns]}


@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_subscription(SubscriptionLevel.STANDARD)),
) -> Dict[str, Any]:
    twin = get_digital_twin()
    recs = await twin.get_recommendations(str(current_user.id))
    return {"recommendations": recs}


@router.post("/metrics", status_code=201)
async def ingest_manual_metrics(
    data: ManualMetricsRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    twin = get_digital_twin()
    metrics = HealthMetrics(
        heart_rate=data.heart_rate,
        steps=data.steps,
        sleep_hours=data.sleep_hours,
        activity_minutes=data.activity_minutes,
        source="manual",
    )
    await twin.ingest_manual(str(current_user.id), metrics)
    return {"status": "saved", "data": asdict(metrics)}
