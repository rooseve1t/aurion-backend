"""Profile preferences endpoints."""
from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database_final import get_db
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/preferences")
async def get_preferences(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    prefs: Dict[str, Any] = dict(current_user.preferences or {})
    return prefs


@router.put("/preferences")
async def update_preferences(
    payload: Dict[str, Any],
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    prefs: Dict[str, Any] = dict(current_user.preferences or {})
    prefs.update(payload)
    current_user.preferences = prefs
    await db.commit()
    return prefs


@router.put("/preferences/voice")
async def update_voice_preferences(
    payload: Dict[str, Any],
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    prefs: Dict[str, Any] = dict(current_user.preferences or {})
    prefs["voice"] = payload
    current_user.preferences = prefs
    await db.commit()
    # Always return voice_persona key — test contract
    result: Dict[str, Any] = dict(payload)
    result["voice_persona"] = payload.get("persona", prefs.get("voice", {}).get("persona", "jarvis"))
    return result
