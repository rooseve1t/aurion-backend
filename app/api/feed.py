"""
Activity Feed API — роутер /api/v2/feed/

GET  /feed               — пагинация по 20 карточек, сортировка created_at DESC
POST /feed/{id}/confirm  — подтвердить карточку
POST /feed/{id}/dismiss  — отклонить карточку
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..database_final import get_db
from ..api.auth import get_current_user
from ..models.user import User
from ..models.feed_card import FeedCard

logger = logging.getLogger("aurion-feed-api")

router = APIRouter(tags=["feed-v2"])

PAGE_SIZE = 20


def _card_to_dict(card: FeedCard) -> Dict[str, Any]:
    return {
        "id": str(card.id),
        "type": card.type,
        "domain": card.domain,
        "title": card.title,
        "body": card.body,
        "priority": card.priority,
        "requiresConfirmation": card.requires_confirmation,
        "confirmedAt": card.confirmed_at.isoformat() if card.confirmed_at else None,
        "dismissedAt": card.dismissed_at.isoformat() if card.dismissed_at else None,
        "createdAt": card.created_at.isoformat() if card.created_at else None,
        "userId": str(card.user_id),
    }


@router.get("/feed")
async def get_feed(
    page: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Получить Activity Feed. Пагинация 20 карточек, новые сверху."""
    offset = page * PAGE_SIZE
    result = await db.execute(
        select(FeedCard)
        .where(FeedCard.user_id == current_user.id)
        .order_by(desc(FeedCard.created_at))
        .offset(offset)
        .limit(PAGE_SIZE)
    )
    cards = result.scalars().all()
    return {
        "page": page,
        "pageSize": PAGE_SIZE,
        "items": [_card_to_dict(c) for c in cards],
        "hasMore": len(cards) == PAGE_SIZE,
    }


@router.post("/feed/{card_id}/confirm")
async def confirm_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Подтвердить карточку."""
    card = await _get_card(card_id, current_user.id, db)
    card.confirmed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(card)

    try:
        from ..services.confirmation_gate import get_confirmation_gate
        await get_confirmation_gate().confirm(card_id, str(current_user.id))
    except Exception:
        pass

    return {"status": "confirmed", "card": _card_to_dict(card)}


@router.post("/feed/{card_id}/dismiss")
async def dismiss_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Отклонить карточку."""
    card = await _get_card(card_id, current_user.id, db)
    card.dismissed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(card)

    try:
        from ..services.confirmation_gate import get_confirmation_gate
        await get_confirmation_gate().cancel(card_id, str(current_user.id))
    except Exception:
        pass

    return {"status": "dismissed", "card": _card_to_dict(card)}


async def _get_card(card_id: str, user_id: Any, db: AsyncSession) -> FeedCard:
    try:
        card_uuid = uuid.UUID(card_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный формат ID.")

    result = await db.execute(
        select(FeedCard)
        .where(FeedCard.id == card_uuid, FeedCard.user_id == user_id)
        .limit(1)
    )
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Карточка не найдена.")
    return card


# ---------------------------------------------------------------------------
# ConfirmationGate — создание запроса подтверждения критического действия
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _BaseModel


class CreateConfirmationRequest(_BaseModel):
    action_type: str
    action_data: dict = {}


@router.post("/feed/confirm-action")
async def create_confirmation_action(
    data: CreateConfirmationRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Создать запрос подтверждения критического действия JARVIS."""
    from ..services.confirmation_gate import get_confirmation_gate
    gate = get_confirmation_gate()
    action_id = await gate.create_confirmation(
        str(current_user.id), data.action_type, data.action_data
    )
    return {"action_id": action_id, "status": "pending", "ttl_seconds": 300}
