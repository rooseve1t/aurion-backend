"""
Финальная версия базы данных SQLAlchemy 2.0 с async поддержкой
"""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB as PGJSONB
import os
import logging
from typing import AsyncGenerator
from dotenv import load_dotenv
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logger = logging.getLogger("aurion-db")

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Кросс-платформенный тип UUID (работает с PostgreSQL и SQLite)
class UUIDType(TypeDecorator):
    """UUID тип, совместимый с PostgreSQL и SQLite"""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(value)

# URL базы данных
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./aurion.db"
)

# Railway и другие платформы передают postgresql:// без asyncpg — исправляем автоматически
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


def _normalize_asyncpg_url(url: str) -> str:
    """
    Нормализация query-параметров для asyncpg.
    Railway/Postgres часто передают `sslmode=require`, тогда как asyncpg
    ожидает `ssl=require`.
    """
    if "postgresql+asyncpg://" not in url:
        return url

    parts = urlsplit(url)
    params = dict(parse_qsl(parts.query, keep_blank_values=True))
    sslmode = params.pop("sslmode", None)
    if sslmode:
        # asyncpg accepts ssl=require|prefer|disable
        params.setdefault("ssl", sslmode)

    normalized_query = urlencode(params)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, normalized_query, parts.fragment))


DATABASE_URL = _normalize_asyncpg_url(DATABASE_URL)

logger.info(f"🗄️ Database driver: {'asyncpg' if 'asyncpg' in DATABASE_URL else 'aiosqlite'}")

# Определяем JSON тип в зависимости от базы данных
JSONType = PGJSONB if 'postgresql' in DATABASE_URL.lower() else JSON

# Настройки движка
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

# Создание движка
# Для SQLite нужны дополнительные настройки для async
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=connect_args if DATABASE_URL.startswith("sqlite") else {}
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
        except Exception as e:
            import traceback
            logger.error(f"Database session error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """
    Инициализация базы данных - создание всех таблиц
    """
    try:
        async with engine.begin() as conn:
            # Если это SQLite, включаем поддержку foreign keys
            if DATABASE_URL.startswith("sqlite"):
                from sqlalchemy import text
                await conn.execute(text("PRAGMA foreign_keys = ON;"))
                # Ensure deterministic test runs on local sqlite test database.
                if "test_" in DATABASE_URL:
                    await conn.run_sync(Base.metadata.drop_all)
            
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database schema initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

async def close_db() -> None:
    """
    Закрытие соединений с базой данных
    """
    try:
        await engine.dispose()
        logger.info("🔌 Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

# Экспортируем метаданные для Alembic
metadata = Base.metadata
