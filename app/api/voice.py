"""
API роутер голосового интерфейса
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..services.voice_service import voice_service
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


class VoicePreviewRequest(BaseModel):
    text: str
    persona: str = "calm"


class VoicePreviewResponse(BaseModel):
    text: str
    persona: str
    emotion: str
    audio: str
    audio_format: str


@router.post("/preview", response_model=VoicePreviewResponse)
async def get_voice_preview(
    request: VoicePreviewRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Предварительный просмотр голоса"""
    
    preview = await voice_service.get_voice_preview(
        text=request.text,
        persona=request.persona
    )
    
    return preview


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    """WebSocket для голосового чата"""
    
    await voice_service.handle_websocket(websocket, "user_id")  # TODO: получить user_id из токена


@router.get("/personas")
async def get_voice_personas() -> Dict[str, Any]:
    """Получение доступных персон голоса"""
    
    personas = {
        "calm": {
            "name": "Спокойный",
            "description": "Ровный и уравновешенный голос",
            "emotion": "neutral"
        },
        "jarvis": {
            "name": "JARVIS",
            "description": "Технологичный и формальный голос",
            "emotion": "analytical"
        },
        "ironic": {
            "name": "Ироничный",
            "description": "С легкой иронией и юмором",
            "emotion": "playful"
        },
        "sarcastic": {
            "name": "Саркастичный",
            "description": "С сарказмом и остроумием",
            "emotion": "sharp"
        }
    }
    
    return {"personas": personas}


@router.get("/settings")
async def get_voice_settings(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получение настроек голоса пользователя"""
    
    # TODO: получить настройки из базы данных
    return {
        "persona": "calm",
        "emotion": "neutral",
        "language": "ru",
        "speed": 1.0,
        "volume": 1.0
    }


@router.put("/settings")
async def update_voice_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Обновление настроек голоса пользователя"""
    
    # TODO: сохранить настройки в базу данных
    
    return {
        "message": "Voice settings updated successfully",
        "settings": settings
    }
