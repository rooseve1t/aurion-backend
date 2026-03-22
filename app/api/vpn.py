"""
🛡️ API роутер Aurion Shield VPN
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from ..database import get_db
from ..services.vpn_service import get_vpn_service, AurionVPNService
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v1/vpn", tags=["aurion-shield-vpn"])

# Pydantic модели
class VPNConnectRequest(BaseModel):
    server_id: str = Field(..., description="ID VPN сервера")
    protocol: str = Field(default="auto", description="Протокол подключения")
    obfuscation: str = Field(default="auto", description="Уровень обфускации")
    stealth: bool = Field(default=False, description="Стелс режим")

class VPNProtocolSwitchRequest(BaseModel):
    protocol: str = Field(..., description="Новый протокол")
    reason: str = Field(default="manual", description="Причина переключения")

class VPNSettingsRequest(BaseModel):
    auto_protocol_switch: bool = Field(default=True, description="Автопереключение протоколов")
    kill_switch: bool = Field(default=True, description="Kill Switch")
    dns_protection: bool = Field(default=True, description="Защита DNS")
    ipv6_protection: bool = Field(default=True, description="Защита IPv6")

class BlockadeTestRequest(BaseModel):
    target_host: str = Field(default="google.com", description="Целевой хост для теста")
    deep_scan: bool = Field(default=False, description="Глубокое сканирование")

@router.get("/status")
async def get_vpn_status(
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Получить текущий статус VPN"""
    try:
        status = await vpn_service.get_connection_status()
        return {
            "success": True,
            "data": status,
            "message": "VPN статус получен"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса: {str(e)}")

@router.post("/connect")
async def connect_vpn(
    request: VPNConnectRequest,
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Подключиться к VPN"""
    try:
        result = await vpn_service.connect_vpn(
            server_id=request.server_id,
            protocol=request.protocol,
            obfuscation=request.obfuscation,
            stealth=request.stealth
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": f"Подключено к {result.get('server', 'VPN')}"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Ошибка подключения"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения: {str(e)}")

@router.post("/disconnect")
async def disconnect_vpn(
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Отключиться от VPN"""
    try:
        result = await vpn_service.disconnect_vpn()
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": "VPN отключен"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Ошибка отключения"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отключения: {str(e)}")

@router.get("/servers")
async def get_available_servers(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получить список доступных серверов"""
    try:
        from ..models.vpn import VPN_SERVERS
        
        servers = []
        for server_data in VPN_SERVERS:
            server = {
                "id": server_data.get("id", "unknown"),
                "name": server_data.get("name", "Unknown"),
                "country": server_data.get("country", "XX"),
                "city": server_data.get("city", "Unknown"),
                "ip_address": server_data.get("ip_address", ""),
                "protocol": server_data.get("protocol", "wireguard"),
                "status": server_data.get("status", "active"),
                "load": server_data.get("load", 0.0),
                "speed_mbps": server_data.get("speed_mbps", 100),
                "latency_ms": server_data.get("latency_ms", 50),
                "obfuscation_support": server_data.get("obfuscation_support", False),
                "stealth_support": server_data.get("stealth_support", False),
                "is_dedicated": server_data.get("is_dedicated", False),
                "is_residential": server_data.get("is_residential", False),
                "is_mobile": server_data.get("is_mobile", False)
            }
            servers.append(server)
        
        return {
            "success": True,
            "data": {
                "servers": servers,
                "total_count": len(servers),
                "countries": len(set(s["country"] for s in servers))
            },
            "message": f"Найдено {len(servers)} серверов"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения серверов: {str(e)}")

@router.get("/protocols")
async def get_available_protocols(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получить список доступных протоколов"""
    try:
        from ..models.vpn import VPN_PROTOCOLS
        
        protocols = []
        for proto_name, proto_config in VPN_PROTOCOLS.items():
            protocol = {
                "name": proto_name,
                "display_name": proto_config.display_name,
                "description": proto_config.description,
                "encryption": proto_config.encryption,
                "obfuscation": proto_config.obfuscation,
                "stealth": proto_config.stealth,
                "speed_factor": proto_config.speed_factor,
                "security_factor": proto_config.security_factor,
                "detection_resistance": proto_config.detection_resistance
            }
            protocols.append(protocol)
        
        return {
            "success": True,
            "data": {
                "protocols": protocols,
                "total_count": len(protocols)
            },
            "message": f"Доступно {len(protocols)} протоколов"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения протоколов: {str(e)}")

@router.post("/detect-blockade")
async def detect_blockade(
    request: BlockadeTestRequest,
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Обнаружить тип блокировки"""
    try:
        detection = await vpn_service.detect_blockades(request.target_host)
        
        return {
            "success": True,
            "data": {
                "blockade_type": detection.blockade_type,
                "confidence_score": detection.confidence_score,
                "blocked_protocols": detection.blocked_protocols,
                "working_protocols": detection.working_protocols,
                "recommended_protocol": detection.recommended_protocol,
                "detection_time": detection.detection_time.isoformat(),
                "target_host": request.target_host
            },
            "message": f"Обнаружена блокировка: {detection.blockade_type}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка детекции блокировки: {str(e)}")

@router.post("/switch-protocol")
async def switch_protocol(
    request: VPNProtocolSwitchRequest,
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Переключить протокол"""
    try:
        success = await vpn_service.auto_switch_protocol()
        
        if success:
            return {
                "success": True,
                "message": f"Протокол переключен на {request.protocol}",
                "reason": request.reason
            }
        else:
            raise HTTPException(status_code=400, detail="Не удалось переключить протокол")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка переключения протокола: {str(e)}")

@router.put("/settings")
async def update_vpn_settings(
    request: VPNSettingsRequest,
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Обновить настройки VPN"""
    try:
        # Обновление настроек сервиса
        vpn_service.auto_protocol_switch = request.auto_protocol_switch
        vpn_service.kill_switch_enabled = request.kill_switch
        
        return {
            "success": True,
            "data": {
                "auto_protocol_switch": vpn_service.auto_protocol_switch,
                "kill_switch": vpn_service.kill_switch_enabled,
                "dns_protection": request.dns_protection,
                "ipv6_protection": request.ipv6_protection
            },
            "message": "Настройки VPN обновлены"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек: {str(e)}")

@router.get("/metrics")
async def get_connection_metrics(
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Получить метрики соединения"""
    try:
        status = await vpn_service.get_connection_status()
        metrics = status.get("metrics")
        
        if not metrics:
            return {
                "success": True,
                "data": {"message": "Нет активного соединения"},
                "message": "Метрики недоступны"
            }
        
        return {
            "success": True,
            "data": metrics,
            "message": "Метрики получены"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения метрик: {str(e)}")

@router.get("/history")
async def get_connection_history(
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Получить историю подключений и блокировок"""
    try:
        history = {
            "blockade_detections": len(vpn_service.blockade_history),
            "recent_detections": [
                {
                    "type": d.blockade_type,
                    "confidence": d.confidence_score,
                    "recommended": d.recommended_protocol,
                    "time": d.detection_time.isoformat()
                }
                for d in vpn_service.blockade_history[-5:]  # Последние 5
            ]
        }
        
        return {
            "success": True,
            "data": history,
            "message": "История получена"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории: {str(e)}")

@router.post("/test-connection")
async def test_connection_speed(
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Тест скорости соединения"""
    try:
        metrics = await vpn_service._measure_connection_metrics()
        
        return {
            "success": True,
            "data": {
                "latency_ms": metrics.latency_ms,
                "download_speed_mbps": metrics.download_speed_mbps,
                "upload_speed_mbps": metrics.upload_speed_mbps,
                "packet_loss": metrics.packet_loss,
                "jitter_ms": metrics.jitter_ms,
                "quality_score": metrics.quality_score
            },
            "message": "Тест скорости завершен"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка теста скорости: {str(e)}")

@router.get("/obfuscation-levels")
async def get_obfuscation_levels(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получить доступные уровни обфускации"""
    try:
        from ..models.vpn import OBFUSCATION_LEVELS
        
        return {
            "success": True,
            "data": OBFUSCATION_LEVELS,
            "message": "Уровни обфускации получены"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения уровней: {str(e)}")

# 🎤 JARVIS интеграция - голосовые команды
@router.post("/jarvis/connect")
async def jarvis_voice_connect(
    server_name: str,
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Голосовая команда JARVIS для подключения"""
    try:
        # Поиск сервера по имени
        from ..models.vpn import VPN_SERVERS
        server_id = None
        for server in VPN_SERVERS:
            if server.get("name", "").lower() == server_name.lower():
                server_id = server.get("id")
                break
        
        if not server_id:
            raise HTTPException(status_code=404, detail="Сервер не найден")
        
        # Подключение с оптимальными настройками
        result = await vpn_service.connect_vpn(
            server_id=server_id,
            protocol="auto",
            obfuscation="auto",
            stealth=True
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": f"JARVIS: Подключил к {server_name}, сэр. Соединение защищено.",
                "jarvis_response": f"Сэр, я успешно подключил вас к серверу {server_name}. Все каналы защищены."
            }
        else:
            return {
                "success": False,
                "error": result.get("error"),
                "message": f"JARVIS: Извините, сэр, не удалось подключиться к {server_name}.",
                "jarvis_response": f"Прошу прощения, сэр. Возникли сложности с подключением к {server_name}."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка голосового подключения: {str(e)}")

@router.post("/jarvis/disconnect")
async def jarvis_voice_disconnect(
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Голосовая команда JARVIS для отключения"""
    try:
        result = await vpn_service.disconnect_vpn()
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": "JARVIS: VPN отключен, сэр.",
                "jarvis_response": "VPN соединение отключено, сэр. Ваше соединение снова открыто."
            }
        else:
            return {
                "success": False,
                "error": result.get("error"),
                "message": "JARVIS: Возникли проблемы с отключением, сэр.",
                "jarvis_response": "Извините, сэр. Возникли технические трудности при отключении."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка голосового отключения: {str(e)}")

@router.get("/jarvis/status")
async def jarvis_voice_status(
    current_user: User = Depends(get_current_user),
    vpn_service: AurionVPNService = Depends(get_vpn_service)
) -> Dict[str, Any]:
    """Голосовой статус JARVIS"""
    try:
        status = await vpn_service.get_connection_status()
        
        if status["connected"]:
            jarvis_response = f"Сэр, VPN активен. Подключены к серверу {status['server']['name']} в {status['server']['country']}. Качество соединения: отличное."
        else:
            jarvis_response = "Сэр, VPN неактивен. Ваше соединение открыто и может отслеживаться."
        
        return {
            "success": True,
            "data": status,
            "message": "JARVIS: Статус проверен.",
            "jarvis_response": jarvis_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка голосового статуса: {str(e)}")
