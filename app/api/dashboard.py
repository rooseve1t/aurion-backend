"""
API для конфигурации персонального дашборда пользователя.
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database_final import get_db
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["dashboard"])

DEFAULT_WIDGETS: List[Dict[str, Any]] = [
    {"id": "system",  "type": "system_status", "title": "Статус системы", "order": 0, "visible": True},
    {"id": "agents",  "type": "agents",         "title": "Агенты",         "order": 1, "visible": True},
    {"id": "threats", "type": "threats",         "title": "Угрозы",         "order": 2, "visible": True},
    {"id": "quotes",  "type": "quotes",          "title": "Котировки",      "order": 3, "visible": True},
    {"id": "memory",  "type": "memory_stats",    "title": "Память JARVIS",  "order": 4, "visible": True},
    {"id": "missions","type": "missions",         "title": "Миссии",         "order": 5, "visible": True},
]


@router.get("/config")
async def get_dashboard_config(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Получить конфигурацию дашборда пользователя."""
    prefs: Dict[str, Any] = dict(current_user.preferences or {})
    widgets = prefs.get("dashboard_widgets", DEFAULT_WIDGETS)
    return {"widgets": widgets}


@router.put("/config")
async def save_dashboard_config(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Сохранить конфигурацию дашборда (порядок и видимость виджетов)."""
    widgets = payload.get("widgets", DEFAULT_WIDGETS)

    prefs: Dict[str, Any] = dict(current_user.preferences or {})
    prefs["dashboard_widgets"] = widgets
    current_user.preferences = prefs
    await db.commit()

    return {"status": "saved", "widgets": widgets}
