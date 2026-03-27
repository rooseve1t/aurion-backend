"""
API роутер умного дома
"""
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database_final import get_db
from ..models.device import Device
from ..services.smarthome_service import get_smarthome_service
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["smarthome"])


class DeviceCreate(BaseModel):
    name: str
    device_type: str
    room: str
    protocol: str = "mqtt"
    address: Optional[str] = None
    topic: Optional[str] = None
    capabilities: Optional[List[str]] = None


class DeviceControl(BaseModel):
    command: str
    parameters: Optional[Dict[str, Any]] = None


class BulkControl(BaseModel):
    commands: List[Dict[str, Any]]


class EnergyOptimization(BaseModel):
    constraints: Optional[Dict[str, Any]] = None


@router.post("/devices")
async def add_device(
    device_data: DeviceCreate,
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> Dict[str, Any]:
    """Добавление нового устройства"""
    
    device = await smarthome_service.add_device(
        user_id=str(current_user.id),
        name=device_data.name,
        device_type=device_data.device_type,
        room=device_data.room,
        protocol=device_data.protocol,
        address=device_data.address,
        topic=device_data.topic,
        capabilities=device_data.capabilities
    )
    
    return {
        "id": str(device.id),
        "name": device.name,
        "device_type": device.device_type,
        "room": device.room,
        "protocol": device.protocol,
        "is_online": device.is_online,
        "created_at": device.created_at.isoformat(),
        "message": "Device added successfully"
    }


@router.get("/devices")
async def get_devices(
    room: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> List[Dict[str, Any]]:
    """Получение списка устройств"""
    
    devices = await smarthome_service.get_devices(
        user_id=str(current_user.id),
        room=room
    )
    
    return [
        {
            "id": str(device.id),
            "name": device.name,
            "device_type": device.device_type,
            "room": device.room,
            "protocol": device.protocol,
            "is_online": device.is_online,
            "is_enabled": device.is_enabled,
            "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
            "capabilities": device.capabilities or []
        }
        for device in devices
    ]


@router.get("/devices/{device_id}")
async def get_device_status(
    device_id: str,
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> Dict[str, Any]:
    """Получение статуса устройства"""
    
    status = await smarthome_service.get_device_status(
        user_id=str(current_user.id),
        device_id=device_id
    )
    
    if not status:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return status


@router.post("/devices/{device_id}/control")
async def control_device(
    device_id: str,
    control_data: DeviceControl,
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> Dict[str, Any]:
    """Управление устройством"""
    try:
        UUID(device_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid device id") from exc
    
    result = await smarthome_service.control_device(
        user_id=str(current_user.id),
        device_id=device_id,
        command=control_data.command,
        parameters=control_data.parameters
    )
    
    return result


@router.post("/devices/control/bulk")
async def control_multiple_devices(
    bulk_data: BulkControl,
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> List[Dict[str, Any]]:
    """Групповое управление устройствами"""
    
    results = await smarthome_service.control_multiple_devices(
        user_id=str(current_user.id),
        commands=bulk_data.commands
    )
    
    return results


@router.post("/energy/optimize")
async def optimize_energy_consumption(
    optimization_data: EnergyOptimization,
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> Dict[str, Any]:
    """Оптимизация энергопотребления"""
    
    result = await smarthome_service.optimize_energy_consumption(
        user_id=str(current_user.id),
        constraints=optimization_data.constraints
    )
    
    return result


@router.get("/rooms")
async def get_rooms(
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> List[str]:
    """Получение списка комнат"""
    
    devices = await smarthome_service.get_devices(user_id=str(current_user.id))
    rooms = list(set(device.room for device in devices if device.room))
    
    return sorted(rooms)


@router.get("/devices/types")
async def get_device_types() -> List[Dict[str, Any]]:
    """Получение поддерживаемых типов устройств"""
    
    device_types = [
        {
            "type": "light",
            "name": "Освещение",
            "capabilities": ["power", "brightness", "color"],
            "commands": ["turn_on", "turn_off", "set_brightness", "set_color"]
        },
        {
            "type": "switch",
            "name": "Выключатель",
            "capabilities": ["power"],
            "commands": ["turn_on", "turn_off"]
        },
        {
            "type": "thermostat",
            "name": "Термостат",
            "capabilities": ["temperature", "mode"],
            "commands": ["set_temperature", "set_mode"]
        },
        {
            "type": "lock",
            "name": "Замок",
            "capabilities": ["lock", "battery"],
            "commands": ["lock", "unlock", "get_status"]
        },
        {
            "type": "sensor",
            "name": "Датчик",
            "capabilities": ["motion", "temperature", "humidity"],
            "commands": ["get_status"]
        },
        {
            "type": "camera",
            "name": "Камера",
            "capabilities": ["recording", "motion_detection"],
            "commands": ["start_recording", "stop_recording", "take_snapshot"]
        }
    ]
    
    return device_types


@router.get("/energy/stats")
async def get_energy_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> Dict[str, Any]:
    """Получение статистики энергопотребления"""
    devices = await smarthome_service.get_devices(user_id=str(current_user.id))
    rooms = {device.room for device in devices if device.room}
    current_consumption = sum(device.power_consumption or 0 for device in devices if device.is_enabled)
    daily_consumption = round(current_consumption * 8 / 1000, 2)
    monthly_consumption = round(daily_consumption * 30, 2)

    return {
        "current_consumption": current_consumption,
        "daily_consumption": daily_consumption,
        "monthly_consumption": monthly_consumption,
        "estimated_cost": round(monthly_consumption * 5.0, 2),
        "devices_count": len(devices),
        "rooms_count": len(rooms),
    }


@router.get("/energy")
async def get_energy_stats_compat(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> Dict[str, Any]:
    """Backward-compatible alias for /energy/stats."""
    return await get_energy_stats(
        db=db,
        current_user=current_user,
        smarthome_service=smarthome_service,
    )


@router.delete("/devices/{device_id}")
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    smarthome_service = Depends(get_smarthome_service)
) -> Dict[str, Any]:
    """Удаление устройства"""
    try:
        device_uuid = UUID(device_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid device id") from exc

    result = await db.execute(
        select(Device).where(
            Device.id == device_uuid,
            Device.user_id == current_user.id,
        )
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    await db.delete(device)
    await db.commit()
    return {"message": "Device deleted successfully"}
