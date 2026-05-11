"""
🔗 API эндпоинты для автономного JARVIS
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Set, cast as typing_cast
import asyncio
from datetime import datetime

from ..services.jarvis.autonomous_jarvis import create_autonomous_jarvis_service, AutonomousJarvisService
from ..services.jarvis.autonomy_engine import AutonomyLevel
from ..services.agent_service import get_agent_service, AgentOrchestrator
from ..services.osint_service import get_osint_service, OSINTService

# Хранилище фоновых задач API
_api_background_tasks: Set[asyncio.Task[Any]] = set()

router = APIRouter(tags=["jarvis-autonomy"])

# Хранение активных соединений
active_connections: Dict[str, AutonomousJarvisService] = {}

async def _send_periodic_updates(websocket: WebSocket, service: AutonomousJarvisService):
    """Периодическая отправка метрик и статуса через WebSocket"""
    try:
        while True:
            status = await service.get_autonomy_status()
            evolution_status = {}
            if service.evolution_engine:
                evolution_status = service.evolution_engine.get_status()

            await websocket.send_json({
                "type": "system_update",
                "status": status,
                "evolution": evolution_status,
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(10)  # Обновление каждые 10 секунд
    except Exception as e:
        print(f"Error in periodic updates: {e}")

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket для автономного JARVIS"""
    await websocket.accept()
    
    update_task = None
    try:
        # Создать автономный сервис
        service = await create_autonomous_jarvis_service(websocket, user_id)
        active_connections[user_id] = service
        
        # Отправить приветствие
        autonomy_engine: Any = getattr(service, "autonomy_engine", None)
        autonomy_level_val = 1
        if autonomy_engine:
            current_level: Any = getattr(autonomy_engine, "current_level", None)
            if current_level:
                autonomy_level_val = getattr(current_level, "value", 1)

        await websocket.send_json({
            "type": "connected",
            "message": "Автономный JARVIS готов к работе",
            "autonomy_level": autonomy_level_val
        })
        
        # Запуск периодических обновлений
        update_task = asyncio.create_task(_send_periodic_updates(websocket, service))

        # Обработка сообщений
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "voice_input":
                # Обработка голосового ввода
                audio_data = data.get("audio", "")
                if audio_data:
                    import base64
                    audio_bytes = base64.b64decode(audio_data)
                    
                    result = await service.process_voice_input(
                        audio_bytes, 
                        data.get("context", {})
                    )
                    
                    await websocket.send_json({
                        "type": "voice_response",
                        "data": result
                    })
                    
            elif data.get("type") == "enable_autonomy":
                # Включить автономность
                level = AutonomyLevel(data.get("level", 1))
                result = await service.enable_autonomy(level)
                await websocket.send_json({
                    "type": "autonomy_enabled",
                    "data": result
                })
                
            elif data.get("type") == "disable_autonomy":
                # Отключить автономность
                result = await service.disable_autonomy()
                await websocket.send_json({
                    "type": "autonomy_disabled",
                    "data": result
                })
                
            elif data.get("type") == "get_status":
                # Получить статус
                status = await service.get_autonomy_status()
                await websocket.send_json({
                    "type": "status",
                    "data": status
                })
                
            elif data.get("type") == "trigger_action":
                # Запустить действие
                action_id = data.get("action_id")
                if action_id:
                    result = await service.trigger_autonomous_action(action_id)
                    await websocket.send_json({
                        "type": "action_triggered",
                        "data": result
                    })
                    
    except WebSocketDisconnect:
        if update_task:
            update_task.cancel()
        if user_id in active_connections:
            del active_connections[user_id]
    except Exception as e:
        if update_task:
            update_task.cancel()
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

@router.get("/status/{user_id}")
async def get_autonomy_status(user_id: str):
    """Получить статус автономности"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    service = active_connections[user_id]
    status = await service.get_autonomy_status()
    
    return JSONResponse(content=status)

@router.post("/enable/{user_id}")
async def enable_autonomy(
    user_id: str, 
    level: int = 1
):
    """Включить автономность"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    try:
        autonomy_level = AutonomyLevel(level)
        service = active_connections[user_id]
        result = await service.enable_autonomy(autonomy_level)
        
        return JSONResponse(content=result)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid autonomy level")

@router.post("/disable/{user_id}")
async def disable_autonomy(user_id: str):
    """Отключить автономность"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    service = active_connections[user_id]
    result = await service.disable_autonomy()
    
    return JSONResponse(content=result)

@router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Получить рекомендации по автономности"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    service = active_connections[user_id]
    recommendations = await service.get_autonomy_recommendations()
    
    return JSONResponse(content=recommendations)

@router.post("/trigger/{user_id}")
async def trigger_action(
    user_id: str,
    action_data: Dict[str, str]
):
    """Запустить автономное действие"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    action_id = action_data.get("action_id")
    if not action_id:
        raise HTTPException(status_code=400, detail="action_id required")
        
    service = active_connections[user_id]
    result = await service.trigger_autonomous_action(action_id)
    
    return JSONResponse(content=result)

@router.put("/preferences/{user_id}")
async def set_preferences(
    user_id: str,
    preferences: Dict[str, Any]
):
    """Установить предпочтения автономности"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    service = active_connections[user_id]
    result = await service.set_autonomy_preferences(preferences)
    
    return JSONResponse(content=result)

@router.get("/actions/{user_id}")
async def get_available_actions(user_id: str):
    """Получить список доступных действий"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    service = active_connections[user_id]
    autonomy_engine: Any = getattr(service, "autonomy_engine", None)
    registered_actions: Dict[str, Any] = {}
    if autonomy_engine:
        registered_actions = typing_cast(Dict[str, Any], getattr(autonomy_engine, "registered_actions", {}))
    
    actions: List[Dict[str, Any]] = []
    for action_id, action in registered_actions.items():
        actions.append({
            "id": action_id,
            "type": str(getattr(getattr(action, "action_type", None), "value", "unknown")),
            "description": str(getattr(action, "description", "")),
            "priority": int(getattr(action, "priority", 0)),
            "risk_level": str(getattr(action, "risk_level", "low")),
            "estimated_time": int(getattr(action, "estimated_time", 0)),
            "autonomy_required": int(getattr(getattr(action, "autonomy_required", None), "value", 1))
        })
    
    return JSONResponse(content={
        "available_actions": actions,
        "total_actions": len(actions)
    })

@router.get("/history/{user_id}")
async def get_action_history(user_id: str, limit: int = 50):
    """Получить историю действий"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    service = active_connections[user_id]
    autonomy_engine: Any = getattr(service, "autonomy_engine", None)
    history: List[Any] = []
    if autonomy_engine:
        history = typing_cast(List[Any], getattr(autonomy_engine, "action_history", []))
    
    selected_history = history[-limit:] if history else []
    
    return JSONResponse(content={
        "history": selected_history,
        "total_actions": len(selected_history)
    })

@router.get("/metrics/{user_id}")
async def get_system_metrics(user_id: str):
    """Получить системные метрики"""
    if user_id not in active_connections:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    service = active_connections[user_id]
    autonomy_engine: Any = getattr(service, "autonomy_engine", None)
    metrics = {}
    if autonomy_engine:
        metrics = getattr(autonomy_engine, "system_metrics", {})
    
    return JSONResponse(content=metrics)

@router.post("/protocol/legion/{user_id}")
async def activate_legion(
    user_id: str,
    goal_data: Dict[str, str],
    agent_service: AgentOrchestrator = Depends(get_agent_service)
):
    """Активация протокола 'Легион' (Stage 14)"""
    goal = goal_data.get("goal")
    if not goal:
        raise HTTPException(status_code=400, detail="Goal required")
        
    result = await agent_service.activate_legion_protocol(user_id, goal)
    return JSONResponse(content=result)

@router.post("/guardian/protect/{user_id}")
async def start_guardian_protection(
    user_id: str,
    osint_service: OSINTService = Depends(get_osint_service)
):
    """Запуск активной защиты Guardian (Stage 14)"""
    # Запускаем в фоновом режиме
    task: asyncio.Task[Any] = asyncio.create_task(osint_service.start_active_guardian(user_id))
    _api_background_tasks.add(task)
    task.add_done_callback(_api_background_tasks.discard)
    return JSONResponse(content={"status": "active_guardian_started", "user_id": user_id})

