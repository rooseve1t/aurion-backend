"""Profile preferences endpoints."""
import asyncio
import logging
from typing import Any, Dict, List
from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database_final import get_db
from app.api.auth import get_current_user

logger = logging.getLogger("aurion-profile")

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
    result: Dict[str, Any] = dict(payload)
    result["voice_persona"] = payload.get("persona", prefs.get("voice", {}).get("persona", "jarvis"))
    return result


# v2 endpoints

@router.get("/export")
async def export_user_data(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """GET /api/v2/profile/export — экспорт всех данных пользователя. Требование 6.5"""
    from app.models.feed_card import FeedCard
    from app.models.payment import Subscription
    from app.models.memory import MemoryEntry
    from app.models.evolution_proposal import EvolutionProposal

    user_id = current_user.id

    fc_result = await db.execute(select(FeedCard).where(FeedCard.user_id == user_id))
    feed_cards: List[Dict[str, Any]] = [
        {
            "id": str(fc.id),
            "type": fc.type,
            "domain": fc.domain,
            "title": fc.title,
            "body": fc.body,
            "priority": fc.priority,
            "requires_confirmation": fc.requires_confirmation,
            "confirmed_at": fc.confirmed_at.isoformat() if fc.confirmed_at else None,
            "dismissed_at": fc.dismissed_at.isoformat() if fc.dismissed_at else None,
            "created_at": fc.created_at.isoformat() if fc.created_at else None,
        }
        for fc in fc_result.scalars().all()
    ]

    sub_result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    subscriptions: List[Dict[str, Any]] = [
        {
            "id": str(s.id),
            "status": s.status,
            "is_active": s.is_active,
            "current_period_start": s.current_period_start.isoformat() if s.current_period_start else None,
            "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sub_result.scalars().all()
    ]

    mem_result = await db.execute(select(MemoryEntry).where(MemoryEntry.user_id == user_id))
    memory: List[Dict[str, Any]] = [
        {
            "id": str(m.id),
            "title": m.title,
            "content": m.content,
            "tags": m.tags,
            "categories": m.categories,
            "importance": m.importance,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in mem_result.scalars().all()
    ]

    ep_result = await db.execute(select(EvolutionProposal).where(EvolutionProposal.user_id == user_id))
    evolution_proposals: List[Dict[str, Any]] = [
        {
            "id": str(ep.id),
            "description": ep.description,
            "affected_files": ep.affected_files,
            "status": ep.status,
            "created_at": ep.created_at.isoformat() if ep.created_at else None,
            "resolved_at": ep.resolved_at.isoformat() if ep.resolved_at else None,
        }
        for ep in ep_result.scalars().all()
    ]

    return {
        "user_id": str(user_id),
        "email": current_user.email,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "feed_cards": feed_cards,
        "subscriptions": subscriptions,
        "memory": memory,
        "evolution_proposals": evolution_proposals,
    }


async def _delete_user_data_after_delay(user_id: str, delay_seconds: int = 86400) -> None:
    """Фоновая задача: удаляет все данные пользователя через delay_seconds секунд. Требование 6.4"""
    from app.database_final import AsyncSessionLocal
    from app.models.user import User

    logger.info(f"Запланировано удаление данных пользователя {user_id} через {delay_seconds}s")
    await asyncio.sleep(delay_seconds)

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                await db.delete(user)
                await db.commit()
                logger.info(f"Данные пользователя {user_id} удалены")
            else:
                logger.warning(f"Пользователь {user_id} не найден при удалении")
    except Exception as e:
        logger.error(f"Ошибка удаления данных пользователя {user_id}: {e}")


@router.delete("", status_code=status.HTTP_202_ACCEPTED)
async def delete_account(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """DELETE /api/v2/profile — удаление аккаунта с задержкой 24ч. Требование 6.4"""
    user_id = str(current_user.id)

    current_user.is_active = False
    await db.commit()

    background_tasks.add_task(_delete_user_data_after_delay, user_id, 86400)

    logger.info(f"Аккаунт {user_id} деактивирован, запланировано удаление через 24ч")

    return {
        "message": "Аккаунт деактивирован. Все данные будут удалены в течение 24 часов.",
        "user_id": user_id,
        "scheduled_deletion_hours": 24,
    }
