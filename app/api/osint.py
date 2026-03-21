"""
API роутер OSINT и разведки
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..services.osint_service import get_osint_service
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v1/osint", tags=["osint"])


class IPRequest(BaseModel):
    ip: str


class EmailRequest(BaseModel):
    email: str


class DomainRequest(BaseModel):
    domain: str


@router.post("/ip")
async def search_ip(
    request: IPRequest,
    current_user: User = Depends(get_current_user),
    osint_service = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Поиск информации по IP адресу"""
    
    # Проверка прав доступа (только creator и admin)
    if current_user.role not in ["creator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="OSINT operations require creator or admin role"
        )
    
    result = await osint_service.search_ip(
        user_id=str(current_user.id),
        ip_address=request.ip
    )
    
    return result


@router.post("/email")
async def search_email(
    request: EmailRequest,
    current_user: User = Depends(get_current_user),
    osint_service = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Поиск информации по email адресу"""
    
    # Проверка прав доступа
    if current_user.role not in ["creator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="OSINT operations require creator or admin role"
        )
    
    result = await osint_service.search_email(
        user_id=str(current_user.id),
        email=request.email
    )
    
    return result


@router.post("/domain")
async def search_domain(
    request: DomainRequest,
    current_user: User = Depends(get_current_user),
    osint_service = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Поиск информации по домену"""
    
    # Проверка прав доступа
    if current_user.role not in ["creator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="OSINT operations require creator or admin role"
        )
    
    result = await osint_service.search_domain(
        user_id=str(current_user.id),
        domain=request.domain
    )
    
    return result


@router.get("/limits")
async def get_rate_limits(
    current_user: User = Depends(get_current_user),
    osint_service = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Получение информации о лимитах"""
    
    # TODO: получить текущее использование лимитов из Redis
    
    return {
        "ip_searches": {
            "limit": 100,
            "used": 0,
            "remaining": 100
        },
        "email_searches": {
            "limit": 50,
            "used": 0,
            "remaining": 50
        },
        "domain_searches": {
            "limit": 30,
            "used": 0,
            "remaining": 30
        }
    }


@router.get("/history")
async def get_search_history(
    current_user: User = Depends(get_current_user),
    osint_service = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Получение истории поиска"""
    
    # TODO: получить историю из AuditLog
    
    return {
        "searches": [],
        "total": 0
    }


@router.get("/targets")
async def get_monitored_targets(
    current_user: User = Depends(get_current_user),
    osint_service = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Получение отслеживаемых целей"""
    
    # TODO: получить цели из OSINTTarget
    
    return {
        "targets": [],
        "total": 0
    }


@router.post("/targets")
async def add_monitored_target(
    target_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    osint_service = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Добавление цели для мониторинга"""
    
    # TODO: создать OSINTTarget
    
    return {"message": "Target added for monitoring"}


@router.delete("/targets/{target_id}")
async def remove_monitored_target(
    target_id: str,
    current_user: User = Depends(get_current_user),
    osint_service = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Удаление цели мониторинга"""
    
    # TODO: удалить OSINTTarget
    
    return {"message": "Target removed from monitoring"}
