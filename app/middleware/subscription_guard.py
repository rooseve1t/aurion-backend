"""
SubscriptionGuard — dependency для проверки уровня подписки пользователя.

Использование:
    from app.middleware.subscription_guard import require_subscription, SubscriptionLevel

    @router.get("/premium-feature")
    async def premium(
        _: None = Depends(require_subscription(SubscriptionLevel.PREMIUM))
    ):
        ...
"""
from enum import Enum
from typing import Optional
import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database_final import get_db
from ..api.auth import get_current_user
from ..models.user import User
from ..models.payment import Subscription

logger = logging.getLogger("aurion-subscription-guard")


class SubscriptionLevel(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


# Числовой порядок уровней для сравнения
_LEVEL_ORDER: dict[str, int] = {
    SubscriptionLevel.BASIC: 0,
    SubscriptionLevel.STANDARD: 1,
    SubscriptionLevel.PREMIUM: 2,
}

# Маппинг имён тарифов из БД на уровень подписки
_TARIFF_NAME_MAP: dict[str, SubscriptionLevel] = {
    "basic": SubscriptionLevel.BASIC,
    "free": SubscriptionLevel.BASIC,
    "standard": SubscriptionLevel.STANDARD,
    "pro": SubscriptionLevel.STANDARD,
    "premium": SubscriptionLevel.PREMIUM,
    "ultimate": SubscriptionLevel.PREMIUM,
}


async def _get_user_subscription_level(
    user: User,
    db: AsyncSession,
) -> SubscriptionLevel:
    """Определить уровень подписки пользователя из БД."""
    try:
        result = await db.execute(
            select(Subscription)
            .where(
                Subscription.user_id == user.id,
                Subscription.is_active == True,  # noqa: E712
            )
            .order_by(Subscription.current_period_end.desc())
            .limit(1)
        )
        subscription = result.scalar_one_or_none()

        if subscription is None:
            return SubscriptionLevel.BASIC

        tariff_name: Optional[str] = None
        if subscription.tariff:
            tariff_name = subscription.tariff.name.lower()

        if tariff_name and tariff_name in _TARIFF_NAME_MAP:
            return _TARIFF_NAME_MAP[tariff_name]

        return SubscriptionLevel.BASIC

    except Exception as exc:
        logger.warning(f"Не удалось получить подписку пользователя {user.id}: {exc}")
        return SubscriptionLevel.BASIC


def require_subscription(min_level: SubscriptionLevel):
    """
    FastAPI dependency-фабрика для защиты эндпоинтов по уровню подписки.

    Пример:
        Depends(require_subscription(SubscriptionLevel.STANDARD))
    """
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        user_level = await _get_user_subscription_level(current_user, db)

        if _LEVEL_ORDER[user_level] < _LEVEL_ORDER[min_level]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Требуется подписка «{min_level.value}». "
                    f"Ваш текущий уровень: «{user_level.value}»."
                ),
            )

    return dependency
