"""
API роутер голосового интерфейса
"""
import base64
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from typing import Dict, Any
from pydantic import BaseModel

from ..auth import verify_token
from ..services.voice_service import voice_service
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["voice"])


class VoicePreviewRequest(BaseModel):
    text: str
    persona: str = "calm"


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "default"


class VoicePreviewResponse(BaseModel):
    text: str
    voice_persona: str
    emotion: str
    tts: Dict[str, Any]


@router.post("/preview", response_model=VoicePreviewResponse)
async def get_voice_preview(
    request: VoicePreviewRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Предварительный просмотр голоса"""
    _ = current_user
    preview = await voice_service.get_voice_preview(
        text=request.text,
        persona=request.persona
    )

    preview_text = preview["text"]
    if not preview_text.startswith("Анализ завершён."):
        preview_text = f"Анализ завершён. {preview_text}"

    return {
        "text": preview_text,
        "voice_persona": preview["persona"],
        "emotion": preview["emotion"],
        "tts": {
            "provider": "edge-tts" if preview.get("audio") else "browser-fallback",
            "audio_b64": preview.get("audio"),
            "mime_type": "audio/mpeg",
            "emotion": preview["emotion"],
            "persona": preview["persona"],
        },
    }


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    """WebSocket для голосового чата"""
    token = websocket.query_params.get("token", "")
    token_data = verify_token(token)
    if not token_data or not token_data.user_id:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "code": "UNAUTHORIZED",
            "message": "Invalid or expired token",
        })
        await websocket.close(code=1008)
        return

    await voice_service.handle_websocket(websocket, token_data.user_id)


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


@router.post("/synthesize")
async def synthesize_speech(
    request: SynthesizeRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Legacy endpoint for speech synthesis."""
    _ = current_user
    preview = await voice_service.get_voice_preview(text=request.text, persona="calm")
    return {
        "text": preview["text"],
        "audio": preview.get("audio"),
        "voice": request.voice,
    }


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Legacy endpoint for transcription."""
    _ = current_user
    payload = await audio.read()
    if not payload:
        raise HTTPException(status_code=400, detail="audio file is required")

    filename = (audio.filename or "").lower()
    fmt = "wav"
    if filename.endswith(".ogg"):
        fmt = "ogg"
    elif filename.endswith(".mp3"):
        fmt = "mp3"

    text = await voice_service.speech_to_text(payload, fmt)
    return {"text": text, "format": fmt}
