# 🤫 JARVIS WHISPER MODE - API ENDPOINTS

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..database import get_db
from ..services.voice_jarvis_standalone import VoiceJarvisStandalone
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v1/voice/jarvis", tags=["jarvis-whisper"])

# Pydantic модели
class VoiceModeRequest(BaseModel):
    mode: str  # normal, whisper, soft, energetic

class WhisperTextRequest(BaseModel):
    text: str

class UserContext(BaseModel):
    tired: Optional[bool] = False
    sleep_mode: Optional[bool] = False
    stress_level: Optional[int] = 0  # 0-10

# Глобальный экземпляр JARVIS
jarvis = VoiceJarvisStandalone()

@router.get("/status")
async def get_voice_status(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Получить текущий статус голосовой системы"""
    try:
        status = jarvis.get_voice_status()
        return {
            "success": True,
            "data": status,
            "message": f"Текущий режим: {status['current_mode']}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса: {str(e)}")

@router.post("/mode")
async def set_voice_mode(
    request: VoiceModeRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Установить режим голоса"""
    try:
        jarvis.set_voice_mode(request.mode)
        return {
            "success": True,
            "message": f"Режим голоса изменен на: {request.mode}",
            "current_mode": jarvis.voice_mode
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка установки режима: {str(e)}")

@router.post("/whisper")
async def speak_whisper(
    request: WhisperTextRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Принудительно сказать шепотом"""
    try:
        audio_data = await jarvis.speak_whisper(request.text)
        return {
            "success": True,
            "message": "Сгенерировано шепотом",
            "audio_data": audio_data.hex() if audio_data else None,
            "text": request.text,
            "mode": "whisper"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации шепота: {str(e)}")

@router.post("/soft")
async def speak_soft(
    request: WhisperTextRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Принудительно сказать мягко"""
    try:
        audio_data = await jarvis.speak_soft(request.text)
        return {
            "success": True,
            "message": "Сгенерировано мягким голосом",
            "audio_data": audio_data.hex() if audio_data else None,
            "text": request.text,
            "mode": "soft"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации мягкого голоса: {str(e)}")

@router.post("/process")
async def process_with_context(
    audio_data: bytes,
    user_context: Optional[UserContext] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Обработать голосовое сообщение с учетом контекста"""
    try:
        context_dict = user_context.dict() if user_context else {}
        
        result = await jarvis.process_voice_message(
            audio_data, 
            context=None,  # Можно добавить контекст из БД
            user_context=context_dict
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "data": result,
            "message": f"Обработано в режиме: {result.get('voice_mode', 'normal')}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

@router.get("/triggers")
async def get_whisper_triggers(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Получить список триггеров для шепота"""
    try:
        return {
            "success": True,
            "data": {
                "triggers": jarvis.whisper_triggers,
                "night_hours": {
                    "start": jarvis.night_hours_start,
                    "end": jarvis.night_hours_end
                },
                "auto_enabled": True
            },
            "message": "Триггеры шепота получены"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения триггеров: {str(e)}")

@router.post("/test-whisper")
async def test_whisper_mode(
    request: WhisperTextRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Тестировать детектор шепота"""
    try:
        should_whisper = jarvis.detect_whisper_context(request.text)
        
        return {
            "success": True,
            "data": {
                "text": request.text,
                "should_whisper": should_whisper,
                "current_hour": datetime.now().hour,
                "contains_trigger": any(trigger in request.text.lower() for trigger in jarvis.whisper_triggers)
            },
            "message": f"Текст {'потребует' if should_whisper else 'не потребует'} шепота"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка тестирования: {str(e)}")
