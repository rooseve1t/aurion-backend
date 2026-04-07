"""
🚨 Emergency Protocol API
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..api.auth import get_current_user

logger = logging.getLogger("api-emergency")
router = APIRouter(prefix="/jarvis/emergency", tags=["emergency"])


class ResolveRequest(BaseModel):
    incident_id: str


@router.get("/incidents")
async def list_incidents(
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """Получить список активных аварийных инцидентов"""
    try:
        from ..services.jarvis.emergency_protocol import get_emergency_protocol
        ep = get_emergency_protocol()
        incidents = ep.get_active_incidents()
        return {"incidents": incidents, "count": len(incidents)}
    except Exception as e:
        logger.error(f"Failed to list incidents: {e}")
        return {"incidents": [], "count": 0}


@router.post("/resolve/{incident_id}")
async def resolve_incident(
    incident_id: str,
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """Закрыть аварийный инцидент"""
    try:
        from ..services.jarvis.emergency_protocol import get_emergency_protocol
        ep = get_emergency_protocol()
        resolved = ep.resolve_incident(incident_id)
        if not resolved:
            raise HTTPException(status_code=404, detail="Инцидент не найден")
        return {"status": "resolved", "incident_id": incident_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_emergency(
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """Тестовый запуск аварийного протокола (только dev)"""
    import os
    if os.getenv("ENV", "development") not in ("development", "dev", "test"):
        raise HTTPException(status_code=403, detail="Доступно только в dev-среде")

    try:
        from ..services.jarvis.emergency_protocol import get_emergency_protocol
        ep = get_emergency_protocol()
        triggered = await ep.evaluate_and_trigger(
            failed_service="test_service",
            failure_count=3,
            system_metrics={"cpu_percent": 50, "memory_percent": 50},
            user_id=str(current_user.id),
            redis_client=None,
            autonomy_engine=None,
        )
        return {"triggered": triggered, "message": "Тестовый аварийный протокол выполнен"}
    except Exception as e:
        logger.error(f"Test emergency failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
