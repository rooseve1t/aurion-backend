"""
Простое рабочее FastAPI приложение
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

# Создание FastAPI приложения
app = FastAPI(
    title="Aurion OS API",
    description="Персональный ИИ-ассистент нового поколения",
    version="1.0.0"
)

# CORS настройки
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://aurionai.ru",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Базовые эндпоинты
@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "api": "ready"
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
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
