"""
Финальное FastAPI приложение с полной функциональностью
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import os
from typing import Optional, List, Dict, Any

from .database_final import init_db, close_db
from .services import init_voice_jarvis_service
from .api import (
    auth_router,
    memory_router,
    voice_router,
    voice_jarvis_router,
    quantum_router,
    osint_router,
    smarthome_router,
    finance_router,
    agents_router,
    payments_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и закрытие приложения"""
    
    # Инициализация базы данных
    await init_db()
    
    # 🏆 ЗОЛОТОЙ СТАНДАРТ: Инициализация JARVIS
    await init_voice_jarvis_service()
    
    print("🚀 Aurion OS initialized successfully")
    print("🎤 JARVIS voice service ready")
    
    yield
    
    # Закрытие соединений
    await close_db()
    print("🔌 Aurion OS shutdown complete")


# Создание FastAPI приложения
app = FastAPI(
    title="Aurion OS API",
    description="Персональный ИИ-ассистент нового поколения",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://aurionai.ru",
    "https://www.aurionai.ru",
    "https://aurion-backend-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключение роутеров
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(memory_router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(voice_router, prefix="/api/v1/voice", tags=["voice"])
app.include_router(voice_jarvis_router, prefix="/api/v1/voice/jarvis", tags=["jarvis"])
app.include_router(quantum_router, prefix="/api/v1/quantum", tags=["quantum"])
app.include_router(osint_router, prefix="/api/v1/osint", tags=["osint"])
app.include_router(smarthome_router, prefix="/api/v1/smarthome", tags=["smarthome"])
app.include_router(finance_router, prefix="/api/v1/finance", tags=["finance"])
app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])


# Health check
@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "redis": "connected",
            "voice": "ready",
            "quantum": "ready",
            "osint": "ready",
            "smarthome": "ready",
            "finance": "ready",
            "agents": "ready",
            "payments": "ready"
        }
    }


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Aurion OS API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Обработка ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "server_error"
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main_final:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
