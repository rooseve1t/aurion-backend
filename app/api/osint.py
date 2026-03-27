"""
API роутер OSINT и разведки
"""
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from ..services.osint_service import get_osint_service, OSINTService
from ..api.auth import get_current_user
from ..models.user import User

# Хранилище для фоновых задач OSINT
_osint_tasks: set = set()

router = APIRouter(tags=["osint"])


class IPRequest(BaseModel):
    ip: str


class EmailRequest(BaseModel):
    email: str


class DomainRequest(BaseModel):
    domain: str


@router.post("/ip", response_model=None)
async def search_ip(
    request: IPRequest,
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
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


@router.get("/ip/{ip}", response_model=None)
async def search_ip_compat(
    ip: str,
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Backward-compatible GET endpoint for IP search."""
    return await search_ip(
        request=IPRequest(ip=ip),
        current_user=current_user,
        osint_service=osint_service,
    )


@router.post("/email", response_model=None)
async def search_email(
    request: EmailRequest,
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
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


@router.get("/email/{email}", response_model=None)
async def search_email_compat(
    email: str,
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Backward-compatible GET endpoint for email search."""
    return await search_email(
        request=EmailRequest(email=email),
        current_user=current_user,
        osint_service=osint_service,
    )


@router.post("/domain", response_model=None)
async def search_domain(
    request: DomainRequest,
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
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


@router.get("/limits", response_model=None)
async def get_rate_limits(
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Получение информации о лимитах"""
    
    result = await osint_service.get_rate_limits(user_id=str(current_user.id))
    return result


@router.get("/history", response_model=None)
async def get_search_history(
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> List[Dict[str, Any]]:
    """Получение истории поисков"""
    
    # Mock history
    return [
        {"type": "ip", "query": "8.8.8.8", "timestamp": datetime.now().isoformat()},
        {"type": "domain", "query": "google.com", "timestamp": datetime.now().isoformat()}
    ]


@router.post("/scan/network", response_model=None)
async def start_network_scan(
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Запуск сканирования сети (Sentinel)"""
    
    if current_user.role not in ["creator", "admin"]:
        raise HTTPException(status_code=403, detail="Sentinel access denied")
        
    task = asyncio.create_task(osint_service.run_sentinel_protocol(user_id=str(current_user.id)))
    _osint_tasks.add(task)
    task.add_done_callback(_osint_tasks.discard)
    
    return {"status": "started", "protocol": "Sentinel", "message": "Сэр, сканирование периметра запущено."}


@router.post("/scan/leaks", response_model=None)
async def start_leak_scan(
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Запуск сканирования утечек (Guardian)"""
    
    if current_user.role not in ["creator", "admin"]:
        raise HTTPException(status_code=403, detail="Guardian access denied")
    
    task = asyncio.create_task(osint_service.start_active_guardian(user_id=str(current_user.id)))
    _osint_tasks.add(task)
    task.add_done_callback(_osint_tasks.discard)
    
    return {"status": "started", "protocol": "Guardian", "message": "Протокол Guardian активирован. Проверяю базу данных утечек."}


@router.get("/targets", response_model=None)
async def get_monitored_targets(
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Получение отслеживаемых целей"""
    
    # TODO: получить цели из OSINTTarget
    
    return {
        "targets": [],
        "total": 0
    }


@router.post("/targets", response_model=None)
async def add_monitored_target(
    target_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Добавление цели для мониторинга"""
    
    # TODO: создать OSINTTarget
    _ = target_data
    
    return {"message": "Target added for monitoring"}


@router.delete("/targets/{target_id}", response_model=None)
async def remove_monitored_target(
    target_id: str,
    current_user: User = Depends(get_current_user),
    osint_service: OSINTService = Depends(get_osint_service)
) -> Dict[str, Any]:
    """Удаление цели мониторинга"""
    
    # TODO: удалить OSINTTarget
    _ = target_id
    
    return {"message": "Target removed from monitoring"}
