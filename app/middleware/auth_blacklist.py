"""
Middleware для проверки JWT blacklist (отозванных токенов)
"""
import logging
from typing import Optional
import redis.asyncio as redis
from jose import JWTError, jwt
import os

logger = logging.getLogger("aurion-blacklist")

_redis_client: Optional[redis.Redis] = None


def set_redis_client(client: redis.Redis) -> None:
    global _redis_client
    _redis_client = client


async def add_to_blacklist(jti: str, ttl_seconds: int) -> None:
    """Добавить jti токена в blacklist"""
    if not _redis_client:
        return
    try:
        await _redis_client.setex(f"blacklist:{jti}", ttl_seconds, "1")
    except Exception as e:
        logger.error(f"Failed to add token to blacklist: {e}")


async def is_blacklisted(jti: str) -> bool:
    """Проверить, отозван ли токен"""
    if not _redis_client:
        return False
    try:
        result = await _redis_client.get(f"blacklist:{jti}")
        return result is not None
    except Exception as e:
        logger.error(f"Failed to check blacklist: {e}")
        return False


def extract_jti(token: str) -> Optional[str]:
    """Извлечь jti из токена без проверки подписи"""
    try:
        SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("jti") or payload.get("sub")  # fallback to sub if no jti
    except JWTError:
        return None
