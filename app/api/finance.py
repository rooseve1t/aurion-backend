"""
API роутер финансового модуля
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..services.finance_service import get_finance_service
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v1/finance", tags=["finance"])


class BankConnectRequest(BaseModel):
    bank_code: str
    redirect_uri: Optional[str] = None


class OAuthCompleteRequest(BaseModel):
    connection_id: str
    code: str


@router.post("/connect")
async def connect_bank(
    request: BankConnectRequest,
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> Dict[str, Any]:
    """Подключение банка"""
    
    result = await finance_service.connect_bank(
        user_id=str(current_user.id),
        bank_code=request.bank_code,
        redirect_uri=request.redirect_uri
    )
    
    return result


@router.post("/oauth/complete")
async def complete_oauth(
    request: OAuthCompleteRequest,
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> Dict[str, Any]:
    """Завершение OAuth процесса"""
    
    result = await finance_service.complete_oauth(
        connection_id=request.connection_id,
        code=request.code
    )
    
    return result


@router.get("/accounts")
async def get_accounts(
    bank_code: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> List[Dict[str, Any]]:
    """Получение банковских счетов"""
    
    accounts = await finance_service.get_accounts(
        user_id=str(current_user.id),
        bank_code=bank_code
    )
    
    return accounts


@router.get("/transactions")
async def get_transactions(
    account_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> Dict[str, Any]:
    """Получение транзакций"""
    
    transactions = await finance_service.get_transactions(
        user_id=str(current_user.id),
        account_id=account_id,
        limit=limit,
        offset=offset,
        category=category
    )
    
    return transactions


@router.get("/analytics")
async def get_analytics(
    period_days: int = 30,
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> Dict[str, Any]:
    """Получение финансовой аналитики"""
    
    analytics = await finance_service.get_analytics(
        user_id=str(current_user.id),
        period_days=period_days
    )
    
    return analytics


@router.get("/tips")
async def get_financial_tips(
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> List[Dict[str, Any]]:
    """Получение финансовых советов"""
    
    tips = await finance_service.get_financial_tips(str(current_user.id))
    
    return tips


@router.post("/sync")
async def sync_bank_data(
    bank_code: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> Dict[str, Any]:
    """Синхронизация данных с банками"""
    
    result = await finance_service.sync_bank_data(
        user_id=str(current_user.id),
        bank_code=bank_code
    )
    
    return result


@router.get("/connections")
async def get_bank_connections(
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> List[Dict[str, Any]]:
    """Получение подключенных банков"""
    
    # TODO: реализовать получение подключений
    
    return []


@router.delete("/connections/{connection_id}")
async def disconnect_bank(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> Dict[str, Any]:
    """Отключение банка"""
    
    # TODO: реализовать отключение
    
    return {"message": "Bank disconnected successfully"}


@router.get("/categories")
async def get_transaction_categories(
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> List[Dict[str, Any]]:
    """Получение категорий транзакций"""
    
    categories = [
        {"name": "Продукты", "icon": "shopping-cart", "color": "#10B981"},
        {"name": "Транспорт", "icon": "car", "color": "#3B82F6"},
        {"name": "Рестораны", "icon": "utensils", "color": "#F59E0B"},
        {"name": "Здоровье", "icon": "heart", "color": "#EF4444"},
        {"name": "Развлечения", "icon": "gamepad", "color": "#8B5CF6"},
        {"name": "Жилье", "icon": "home", "color": "#6B7280"},
        {"name": "Одежда", "icon": "shirt", "color": "#EC4899"},
        {"name": "Связь", "icon": "phone", "color": "#14B8A6"},
        {"name": "Образование", "icon": "book", "color": "#F97316"},
        {"name": "Прочее", "icon": "more-horizontal", "color": "#9CA3AF"}
    ]
    
    return categories


@router.get("/budget")
async def get_budget(
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> Dict[str, Any]:
    """Получение бюджета"""
    
    # TODO: реализовать получение бюджета
    
    return {
        "monthly_budget": 100000,
        "categories": {
            "Продукты": {"budget": 30000, "spent": 25000},
            "Транспорт": {"budget": 15000, "spent": 12000},
            "Рестораны": {"budget": 10000, "spent": 15000},
            "Здоровье": {"budget": 5000, "spent": 3000}
        },
        "total_spent": 55000,
        "remaining": 45000
    }


@router.put("/budget")
async def update_budget(
    budget_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    finance_service = Depends(get_finance_service)
) -> Dict[str, Any]:
    """Обновление бюджета"""
    
    # TODO: реализовать обновление бюджета
    
    return {"message": "Budget updated successfully"}
