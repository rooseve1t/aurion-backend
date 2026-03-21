"""
Финальная версия базы данных SQLAlchemy 2.0 с async поддержкой
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from typing import AsyncGenerator

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# URL базы данных
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://aurion:password@localhost:5432/aurion"
)

# Создание движка
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Включить SQL логи для разработки
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии базы данных
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db() -> None:
    """
    Инициализация базы данных - создание всех таблиц
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    """
    Закрытие соединений с базой данных
    """
    await engine.dispose()

# Экспортируем метаданные для Alembic
metadata = Base.metadata
