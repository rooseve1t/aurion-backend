"""
SmartHome v2 — дополнительные эндпоинты /api/v2/smarthome/

POST /scan      — запустить сканирование IoT-устройств
POST /register  — зарегистрировать найденное устройство
"""
import logging
from dataclasses import asdict
from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..api.auth import get_current_user
from ..models.user import User
from ..services.device_discovery import get_device_discovery

logger = logging.getLogger("aurion-smarthome-v2")

router = APIRouter(tags=["smarthome-v2"])


class RegisterDeviceRequest(BaseModel):
    name: str
    ip: str
    mac: str = ""
    device_type: str = "unknown"
    protocol: str = "manual"
    properties: dict = {}


@router.post("/scan")
async def scan_devices(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Сканировать сеть через mDNS и UPnP. Найденные устройства появятся в Activity Feed."""
    discovery = get_device_discovery()
    devices = await discovery.scan(str(current_user.id))
    return {
        "found": len(devices),
        "devices": [asdict(d) for d in devices],
        "message": "Найденные устройства добавлены в ленту для подтверждения.",
    }


@router.post("/register")
async def register_device(
    data: RegisterDeviceRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Зарегистрировать устройство вручную или после подтверждения из Activity Feed."""
    discovery = get_device_discovery()
    success = await discovery.register_device(str(current_user.id), data.model_dump())
    if success:
        return {"status": "registered", "device": data.model_dump()}
    return {"status": "error", "message": "Не удалось зарегистрировать устройство."}
