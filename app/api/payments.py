"""
API роутер платежной системы и подписок
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel

from ..database import AsyncSessionLocal
from ..api.auth import get_current_user, get_db_session
from ..models.user import User

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


class SubscribeRequest(BaseModel):
    tariff_id: str


class WebhookData(BaseModel):
    event: str
    object: Dict[str, Any]


@router.get("/tariffs")
async def get_tariffs(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Получение доступных тарифов"""
    
    # TODO: получить тарифы из базы данных
    tariffs = [
        {
            "id": "free",
            "name": "Free",
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
                "agents": False
            },
            "is_popular": False,
            "badge": None
        },
        {
            "id": "basic",
            "name": "Basic",
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
                "agents": True
            },
            "is_popular": True,
            "badge": "popular"
        },
        {
            "id": "pro",
            "name": "Pro",
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
                "agents": True
            },
            "is_popular": False,
            "badge": "recommended"
        }
    ]
    
    return tariffs


@router.post("/subscribe")
async def create_subscription(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Создание подписки"""
    
    # TODO: интеграция с ЮKassa
    # Заглушка для демонстрации
    
    return {
        "status": "pending",
        "payment_url": "https://yoomoney.ru/checkout/payments/v2/contract?contract=12345",
        "payment_id": "payment_12345",
        "tariff_id": request.tariff_id,
        "amount": 990,
        "currency": "RUB"
    }


@router.get("/subscriptions")
async def get_user_subscriptions(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Получение подписок пользователя"""
    
    # TODO: получить подписки из базы данных
    
    return []


@router.get("/subscriptions/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получение текущей подписки"""
    
    # TODO: получить текущую подписку из базы данных
    
    return {
        "status": "active",
        "tariff": {
            "id": "basic",
            "name": "Basic",
            "display_name": "Базовый",
            "price": 990,
            "currency": "RUB"
        },
        "current_period_start": "2024-01-01T00:00:00Z",
        "current_period_end": "2024-02-01T00:00:00Z",
        "auto_renew": True,
        "next_billing_amount": 990,
        "features": {
            "voice": True,
            "memory_limit": 1000,
            "devices_limit": 20,
            "osint": False,
            "quantum": False,
            "finance": True,
            "agents": True
        }
    }


@router.post("/subscriptions/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Отмена подписки"""
    
    # TODO: отмена подписки в платежной системе и базе данных
    
    return {"message": "Subscription cancelled successfully"}


@router.post("/subscriptions/reactivate")
async def reactivate_subscription(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    "Реактивация подписки"""
    
    # TODO: реактивация подписки
    
    return {"message": "Subscription reactivated successfully"}


@router.get("/payments")
async def get_payment_history(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Получение истории платежей"""
    
    # TODO: получить платежи из базы данных
    
    return []


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
