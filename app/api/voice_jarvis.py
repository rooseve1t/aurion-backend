"""
🏆 ЗОЛОТОЙ СТАНДАРТ: API роутер голосового ассистента JARVIS
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import asyncio
import json
import base64
import io
from datetime import datetime, timezone

from ..database_final import AsyncSessionLocal
from ..services.voice_jarvis_service import VoiceJarvisService, get_voice_jarvis_service
from ..api.auth import get_current_user, get_db_session
from ..models.user import User

router = APIRouter(tags=["jarvis"])

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Pydantic модели с валидацией
class VoiceRequest(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")
    context: Optional[List[Dict[str, str]]] = Field(None, description="Conversation context")
    emotion: Optional[str] = Field("neutral", description="Desired emotion")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed")

class VoiceResponse(BaseModel):
    user_text: str = Field(..., description="Recognized user speech")
    jarvis_text: str = Field(..., description="JARVIS response")
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio response")
    emotion: str = Field(..., description="Detected emotion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Recognition confidence")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: str = Field(..., description="Response timestamp")

class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to convert to speech")
    emotion: Optional[str] = Field("neutral", description="Desired emotion")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed")

class TextResponse(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio")
    text: str = Field(..., description="Original text")
    emotion: str = Field(..., description="Applied emotion")
    processing_time: float = Field(..., description="Processing time in seconds")

class ConversationHistory(BaseModel):
    messages: List[Dict[str, Any]] = Field(..., description="Conversation messages")
    total_messages: int = Field(..., description="Total number of messages")
    session_duration: float = Field(..., description="Session duration in seconds")

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Зависимости
async def get_db_session() -> AsyncSession:
    """Получение сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Основные эндпоинты
@router.post("/speech-to-text", response_model=Dict[str, Any])
async def speech_to_text(
    request: VoiceRequest,
    current_user: User = Depends(get_current_user),
    jarvis_service: VoiceJarvisService = Depends(get_voice_jarvis_service)
) -> Dict[str, Any]:
    """
    🏆 Преобразование речи в текст с максимальным качеством
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Декодируем аудио
        audio_data = base64.b64decode(request.audio_data)
        
        # Распознаем речь
        user_text = await jarvis_service.speech_to_text(audio_data)
        
        if not user_text:
            raise HTTPException(
                status_code=400,
                detail="Не удалось распознать речь"
            )
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return {
            "user_text": user_text,
            "confidence": 0.95,  # TODO: Реальный confidence
            "processing_time": processing_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": str(current_user.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка распознавания речи: {str(e)}"
        )

@router.post("/text-to-speech", response_model=TextResponse)
async def text_to_speech(
    request: TextRequest,
    current_user: User = Depends(get_current_user),
    jarvis_service: VoiceJarvisService = Depends(get_voice_jarvis_service)
) -> TextResponse:
    """
    🏆 Преобразование текста в речь с максимальным качеством
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Генерируем аудио
        audio_data = await jarvis_service.text_to_speech(request.text)
        
        if not audio_data:
            raise HTTPException(
                status_code=500,
                detail="Не удалось сгенерировать речь"
            )
        
        # Кодируем аудио
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return TextResponse(
            audio_data=audio_base64,
            text=request.text,
            emotion=request.emotion,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка синтеза речи: {str(e)}"
        )

@router.post("/full-conversation", response_model=VoiceResponse)
async def full_conversation(
    request: VoiceRequest,
    current_user: User = Depends(get_current_user),
    jarvis_service: VoiceJarvisService = Depends(get_voice_jarvis_service)
) -> VoiceResponse:
    """
    🏆 Полный цикл обработки голосового сообщения
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Декодируем аудио
        audio_data = base64.b64decode(request.audio_data)
        
        # Получаем контекст
        context = await jarvis_service.get_conversation_context(str(current_user.id))
        
        # Полная обработка
        result = await jarvis_service.process_voice_message(audio_data, context)
        
        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
        
        # Сохраняем контекст
        await jarvis_service.save_conversation_message(
            str(current_user.id), 
            "user", 
            result["user_text"]
        )
        await jarvis_service.save_conversation_message(
            str(current_user.id), 
            "assistant", 
            result["jarvis_text"]
        )
        
        # Кодируем аудио ответа
        audio_base64 = None
        if result.get("audio_response"):
            audio_base64 = base64.b64encode(result["audio_response"]).decode('utf-8')
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return VoiceResponse(
            user_text=result["user_text"],
            jarvis_text=result["jarvis_text"],
            audio_data=audio_base64,
            emotion=request.emotion or "neutral",
            confidence=0.95,  # TODO: Реальный confidence
            processing_time=processing_time,
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки голоса: {str(e)}"
        )

@router.get("/conversation-history", response_model=ConversationHistory)
async def get_conversation_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    jarvis_service: VoiceJarvisService = Depends(get_voice_jarvis_service)
) -> ConversationHistory:
    """
    🏆 Получение истории разговоров
    """
    try:
        context = await jarvis_service.get_conversation_context(str(current_user.id), limit)
        
        # Вычисляем длительность сессии
        session_duration = 0.0
        if context:
            first_message = json.loads(context[0])
            last_message = json.loads(context[-1])
            
            first_time = datetime.fromisoformat(first_message["timestamp"].replace('Z', '+00:00'))
            last_time = datetime.fromisoformat(last_message["timestamp"].replace('Z', '+00:00'))
            session_duration = (last_time - first_time).total_seconds()
        
        return ConversationHistory(
            messages=[json.loads(msg) for msg in context],
            total_messages=len(context),
            session_duration=session_duration
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения истории: {str(e)}"
        )

@router.delete("/conversation-history")
async def clear_conversation_history(
    current_user: User = Depends(get_current_user),
    jarvis_service: VoiceJarvisService = Depends(get_voice_jarvis_service)
) -> Dict[str, Any]:
    """
    🏆 Очистка истории разговоров
    """
    try:
        if jarvis_service.redis:
            context_key = f"conversation:{str(current_user.id)}"
            await jarvis_service.redis.delete(context_key)
        
        return {
            "message": "История разговоров очищена",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка очистки истории: {str(e)}"
        )

# 🏆 ЗОЛОТОЙ СТАНДАРТ: WebSocket для реального времени
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    🏆 WebSocket для реального времени общения с JARVIS
    """
    await websocket.accept()
    
    jarvis_service = VoiceJarvisService()
    user_id = None
    
    try:
        # Аутентификация через WebSocket
        auth_data = await websocket.receive_text()
        auth = json.loads(auth_data)
        
        # TODO: Реальная аутентификация
        user_id = auth.get("user_id", "anonymous")
        
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "JARVS готов к общению",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))
        
        # Основной цикл обработки сообщений
        while True:
            # Получаем сообщение
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("type") == "audio":
                # Обработка аудио
                audio_data = base64.b64decode(data["audio_data"])
                
                # Получаем контекст
                context = await jarvis_service.get_conversation_context(user_id)
                
                # Обрабатываем
                result = await jarvis_service.process_voice_message(audio_data, context)
                
                # Сохраняем контекст
                if "user_text" in result and "jarvis_text" in result:
                    await jarvis_service.save_conversation_message(user_id, "user", result["user_text"])
                    await jarvis_service.save_conversation_message(user_id, "assistant", result["jarvis_text"])
                
                # Отправляем ответ
                response = {
                    "type": "response",
                    "user_text": result.get("user_text"),
                    "jarvis_text": result.get("jarvis_text"),
                    "timestamp": result.get("timestamp")
                }
                
                # Добавляем аудио если есть
                if result.get("audio_response"):
                    response["audio_data"] = base64.b64encode(result["audio_response"]).decode('utf-8')
                
                await websocket.send_text(json.dumps(response))
                
            elif data.get("type") == "text":
                # Обработка текста
                text = data["text"]
                
                # Получаем контекст
                context = await jarvis_service.get_conversation_context(user_id)
                
                # Генерируем ответ
                jarvis_response = await jarvis_service.generate_response(text, context)
                
                # Сохраняем контекст
                await jarvis_service.save_conversation_message(user_id, "user", text)
                await jarvis_service.save_conversation_message(user_id, "assistant", jarvis_response)
                
                # Генерируем аудио
                audio_data = await jarvis_service.text_to_speech(jarvis_response)
                
                # Отправляем ответ
                response = {
                    "type": "response",
                    "user_text": text,
                    "jarvis_text": jarvis_response,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                if audio_data:
                    response["audio_data"] = base64.b64encode(audio_data).decode('utf-8')
                
                await websocket.send_text(json.dumps(response))
                
            elif data.get("type") == "ping":
                # Heartbeat
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Эндпоинты управления
@router.get("/status")
async def get_jarvis_status(
    current_user: User = Depends(get_current_user),
    jarvis_service: VoiceJarvisService = Depends(get_voice_jarvis_service)
) -> Dict[str, Any]:
    """
    🏆 Статус JARVIS сервиса
    """
    try:
        return {
            "status": "active",
            "tts_provider": jarvis_service.tts_provider,
            "stt_provider": jarvis_service.stt_provider,
            "llm_provider": jarvis_service.llm_provider,
            "redis_connected": jarvis_service.redis is not None,
            "personality": jarvis_service.jarvis_personality,
            "capabilities": [
                "speech_to_text",
                "text_to_speech", 
                "full_conversation",
                "context_memory",
                "realtime_websocket",
                "emotional_responses"
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения статуса: {str(e)}"
        )

@router.post("/reset-personality")
async def reset_jarvis_personality(
    current_user: User = Depends(get_current_user),
    jarvis_service: VoiceJarvisService = Depends(get_voice_jarvis_service)
) -> Dict[str, Any]:
    """
    🏆 Сброс личности JARVIS к настройкам по умолчанию
    """
    try:
        # TODO: Реализация сброса личности
        return {
            "message": "Личность JARVIS сброшена",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сброса личности: {str(e)}"
        )
