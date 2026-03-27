"""
API роутер платежной системы и подписок
"""
from datetime import datetime, timedelta, timezone
import os
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select as future_select

from ..api.auth import get_current_user, get_current_user_optional, get_db_session
from ..models.payment import Payment, Subscription, Tariff
from ..models.user import User

router = APIRouter(tags=["payments"])


class SubscribeRequest(BaseModel):
    tariff_id: str


class WebhookData(BaseModel):
    event: str
    object: Dict[str, Any]


DEFAULT_TARIFFS: List[Dict[str, Any]] = [
    {
        "name": "free",
        "display_name": "Бесплатный",
        "description": "Базовый функционал для знакомства",
        "price": 0,
        "currency": "RUB",
        "billing_interval": "month",
        "features": {
            "voice": True,
            "memory_limit": 100,
            "devices_limit": 5,
            "osint": False,
            "quantum": False,
            "finance": False,
            "agents": False,
        },
        "badge": None,
        "sort_order": 0,
    },
    {
        "name": "basic",
        "display_name": "Базовый",
        "description": "Расширенный функционал для повседневного использования",
        "price": 990,
        "currency": "RUB",
        "billing_interval": "month",
        "features": {
            "voice": True,
            "memory_limit": 1000,
            "devices_limit": 20,
            "osint": False,
            "quantum": False,
            "finance": True,
            "agents": True,
        },
        "badge": "popular",
        "sort_order": 1,
    },
    {
        "name": "pro",
        "display_name": "Профессиональный",
        "description": "Полный доступ ко всем возможностям системы",
        "price": 2990,
        "currency": "RUB",
        "billing_interval": "month",
        "features": {
            "voice": True,
            "memory_limit": -1,
            "devices_limit": -1,
            "osint": True,
            "quantum": True,
            "finance": True,
            "agents": True,
        },
        "badge": "recommended",
        "sort_order": 2,
    },
]


async def _ensure_default_tariffs(db: AsyncSession) -> List[Tariff]:
    result = await db.execute(select(Tariff).order_by(Tariff.sort_order, Tariff.price))
    tariffs = result.scalars().all()
    existing_names = {tariff.name for tariff in tariffs}
    
    new_tariffs_added = False

    for raw in DEFAULT_TARIFFS:
        if raw["name"] in existing_names:
            continue
        tariff = Tariff(
            name=raw["name"],
            display_name=raw["display_name"],
            description=raw["description"],
            price=raw["price"],
            currency=raw["currency"],
            billing_interval=raw["billing_interval"],
            features=raw["features"],
            limits={},
            badge=raw["badge"],
            sort_order=raw["sort_order"],
            is_active=True,
            is_public=True,
        )
        db.add(tariff)
        new_tariffs_added = True

    if new_tariffs_added:
        try:
            await db.commit()
        except IntegrityError:
            # Concurrent inserts may race on unique tariff names; reload canonical rows.
            await db.rollback()
        result = await db.execute(select(Tariff).order_by(Tariff.sort_order, Tariff.price))
        tariffs = result.scalars().all()

    return tariffs


def _serialize_tariff(tariff: Tariff) -> Dict[str, Any]:
    return {
        "id": str(tariff.id),
        "name": tariff.name.capitalize(),
        "display_name": tariff.display_name,
        "description": tariff.description,
        "price": tariff.price,
        "currency": tariff.currency,
        "duration_days": 30 if tariff.billing_interval == "month" else 365,
        "billing_interval": tariff.billing_interval,
        "features": tariff.features or {},
        "is_active": tariff.is_active,
        "badge": tariff.badge,
    }


def _serialize_subscription(subscription: Subscription) -> Dict[str, Any]:
    tariff = subscription.tariff
    now = datetime.now(timezone.utc)
    days_left = None
    if subscription.current_period_end:
        end_date = subscription.current_period_end
        # Ensure timezone-aware comparison
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        else:
            end_date = end_date.astimezone(timezone.utc)
        days_left = max(0, (end_date - now).days)

    return {
        "id": str(subscription.id),
        "tariff_id": str(subscription.tariff_id),
        "status": subscription.status,
        "start_date": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
        "end_date": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
        "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        "auto_renew": subscription.auto_renew,
        "cancelled_at": subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
        "created_at": subscription.created_at.isoformat(),
        "days_left": days_left,
        "tariff": _serialize_tariff(tariff) if tariff else None,
        "features": (tariff.features if tariff else {}) or {},
        "next_billing_amount": subscription.next_billing_amount,
    }


def _serialize_payment(payment: Payment) -> Dict[str, Any]:
    return {
        "id": str(payment.id),
        "subscription_id": str(payment.subscription_id) if payment.subscription_id else None,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
        "description": payment.description,
        "created_at": payment.created_at.isoformat(),
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        "provider": payment.provider,
        "payment_method": payment.payment_method,
        "external_id": payment.external_id,
    }


@router.get("/tariffs")
async def get_tariffs(
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> List[Dict[str, Any]]:
    """Получение доступных тарифов"""
    tariffs = await _ensure_default_tariffs(db)
    return [_serialize_tariff(tariff) for tariff in tariffs if tariff.is_public]


@router.post("/subscribe")
async def create_subscription(
    request: SubscribeRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Создание подписки"""
    current_user_id = current_user.id
    tariffs = await _ensure_default_tariffs(db)
    tariff = None

    for item in tariffs:
        if str(item.id) == request.tariff_id or item.name == request.tariff_id.lower():
            tariff = item
            break

    if tariff is None:
        raise HTTPException(status_code=404, detail="Tariff not found")

    # Блокировка активных подписок для предотвращения race condition
    # Используем SELECT FOR UPDATE
    from sqlalchemy import text
    
    # Сначала деактивируем все активные подписки с блокировкой
    await db.execute(
        update(Subscription)
        .where(
            Subscription.user_id == current_user_id,
            Subscription.is_active.is_(True)
        )
        .values(
            is_active=False,
            auto_renew=False,
            status="cancelled",
            cancelled_at=datetime.now(timezone.utc)
        )
        .execution_options(synchronize_session=False)
    )

    now = datetime.now(timezone.utc)
    subscription = Subscription(
        user_id=current_user_id,
        tariff_id=tariff.id,
        status="active" if tariff.price == 0 else "pending",
        is_active=True,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        auto_renew=tariff.price > 0,
        next_billing_amount=tariff.price,
        payment_metadata={"mode": "mock", "provider": "yookassa"},
    )
    db.add(subscription)
    await db.flush()

    payment_status = "succeeded" if tariff.price == 0 else "pending"
    payment = Payment(
        user_id=current_user_id,
        subscription_id=subscription.id,
        provider="yookassa",
        external_id=f"demo-{subscription.id}",
        amount=tariff.price,
        currency=tariff.currency,
        status=payment_status,
        paid=tariff.price == 0,
        description=f"{tariff.display_name} тариф Aurion",
        transaction_metadata={"mode": "mock", "tariff": tariff.name},
        payment_method="card" if tariff.price > 0 else "free",
        payment_method_details={"provider": "yookassa", "mock": True},
        paid_at=now if tariff.price == 0 else None,
        expires_at=now + timedelta(minutes=30) if tariff.price > 0 else None,
    )
    db.add(payment)
    await db.commit()

    confirmation_base = os.getenv("APP_BASE_URL", "https://www.aurionai.ru")
    confirmation_url = (
        f"{confirmation_base}/payments/success?payment_id={payment.id}"
        if tariff.price == 0
        else f"{confirmation_base}/payments/checkout?payment_id={payment.id}"
    )

    return {
        "status": payment_status,
        "payment_url": confirmation_url,
        "confirmation_url": confirmation_url,
        "subscription_id": str(subscription.id),
        "payment_id": str(payment.id),
        "tariff_id": str(tariff.id),
        "tariff_name": tariff.display_name,
        "amount": tariff.price,
        "currency": tariff.currency,
    }


@router.get("/subscriptions")
async def get_user_subscriptions(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Получение подписок пользователя"""
    await _ensure_default_tariffs(db)
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.tariff))
        .where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )
    subscriptions = result.scalars().all()
    return [_serialize_subscription(item) for item in subscriptions]


@router.get("/subscriptions/current")
async def get_current_subscription(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получение текущей подписки"""
    await _ensure_default_tariffs(db)
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.tariff))
        .where(
            Subscription.user_id == current_user.id,
            Subscription.is_active.is_(True),
        )
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalars().first()

    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")

    return _serialize_subscription(subscription)


@router.get("/subscription")
async def get_current_subscription_compat(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Backward-compatible alias for current subscription."""
    return await get_current_subscription(db=db, current_user=current_user)


@router.post("/subscriptions/cancel")
@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Отмена подписки"""
    stmt = (
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )
    if subscription_id:
        try:
            stmt = stmt.where(Subscription.id == UUID(subscription_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid subscription id") from exc

    result = await db.execute(stmt)
    subscription = result.scalars().first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.status = "cancelled"
    subscription.auto_renew = False
    subscription.is_active = False
    subscription.cancelled_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(subscription)

    return {
        "message": "Subscription cancelled successfully",
        "subscription": _serialize_subscription(subscription),
    }


@router.post("/subscription/cancel")
async def cancel_subscription_compat(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Backward-compatible alias for subscription cancellation."""
    return await cancel_subscription(subscription_id=None, db=db, current_user=current_user)


@router.post("/subscriptions/reactivate")
async def reactivate_subscription(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Реактивация подписки"""
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalars().first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.status = "active"
    subscription.auto_renew = True
    subscription.is_active = True
    subscription.cancelled_at = None
    await db.commit()
    await db.refresh(subscription)

    return {
        "message": "Subscription reactivated successfully",
        "subscription": _serialize_subscription(subscription),
    }


@router.get("/payments")
async def get_payment_history(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Получение истории платежей"""
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()
    return {
        "payments": [_serialize_payment(payment) for payment in payments],
        "total": len(payments),
    }


@router.get("/history")
async def get_payment_history_compat(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Backward-compatible alias for payment history."""
    return await get_payment_history(db=db, current_user=current_user)


@router.post("/subscription")
async def create_subscription_compat(
    request: SubscribeRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Backward-compatible alias for subscription creation."""
    return await create_subscription(request=request, db=db, current_user=current_user)


@router.post("/webhook")
async def payment_webhook(
    webhook_data: WebhookData
) -> Dict[str, Any]:
    """Обработка вебхуков от платежной системы"""
    
    # TODO: обработка вебхуков ЮKassa
    event = webhook_data.event
    object_data = webhook_data.object
    
    if event == "payment.succeeded":
        # Успешный платеж
        pass
    elif event == "payment.canceled":
        # Отмена платежа
        pass
    elif event == "subscription.created":
        # Создание подписки
        pass
    elif event == "subscription.updated":
        # Обновление подписки
        pass
    elif event == "subscription.canceled":
        # Отмена подписки
        pass
    
    return {"status": "ok"}


@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получение статистики использования"""
    
    # TODO: получить статистику использования
    
    return {
        "memory_entries": 245,
        "memory_limit": 1000,
        "devices_count": 8,
        "devices_limit": 20,
        "api_calls": 15420,
        "api_calls_limit": 50000,
        "quantum_jobs": 2,
        "quantum_jobs_limit": 0,  # Нет в тарифе
        "osint_requests": 0,
        "osint_requests_limit": 0  # Нет в тарифе
    }


@router.get("/billing")
async def get_billing_info(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получение биллинговой информации"""
    
    # TODO: получить биллинговую информацию
    
    return {
        "next_payment_date": "2024-02-01T00:00:00Z",
        "next_payment_amount": 990,
        "currency": "RUB",
        "payment_method": {
            "type": "card",
            "last4": "1234",
            "brand": "visa",
            "exp_month": 12,
            "exp_year": 2025
        },
        "billing_history": [
            {
                "date": "2024-01-01T00:00:00Z",
                "amount": 990,
                "currency": "RUB",
                "status": "succeeded",
                "description": "Basic тариф - Январь 2024"
            }
        ]
    }


@router.post("/payment-methods")
async def add_payment_method(
    payment_method_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Добавление способа оплаты"""
    
    # TODO: интеграция с платежной системой
    
    return {"message": "Payment method added successfully"}


@router.get("/payment-methods")
async def get_payment_methods(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Получение способов оплаты"""
    
    # TODO: получить способы оплаты
    
    return []


@router.delete("/payment-methods/{method_id}")
async def delete_payment_method(
    method_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Удаление способа оплаты"""
    
    # TODO: удаление способа оплаты
    
    return {"message": "Payment method deleted successfully"}
