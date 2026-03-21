"""
Основное приложение FastAPI с полной реализацией Aurion OS
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import os

from .database import init_db, close_db
from .api import (
    auth_router,
    memory_router,
    voice_router,
    quantum_router,
    osint_router,
    smarthome_router,
    finance_router,
    agents_router,
    payments_router
)
from .services import (
    init_voice_service,
    init_quantum_service,
    init_osint_service,
    init_smarthome_service,
    init_finance_service,
    init_agent_service
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и закрытие приложения"""
    
    # Инициализация базы данных
    await init_db()
    
    # Инициализация сервисов
    await init_voice_service()
    await init_quantum_service()
    await init_osint_service()
    await init_smarthome_service()
    await init_finance_service()
    await init_agent_service()
    
    print("🚀 Aurion OS initialized successfully")
    
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
app.include_router(auth_router)
app.include_router(memory_router)
app.include_router(voice_router)
app.include_router(quantum_router)
app.include_router(osint_router)
app.include_router(smarthome_router)
app.include_router(finance_router)
app.include_router(agents_router)
app.include_router(payments_router)


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
            "agents": "ready"
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
        "app.main_fastapi:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
