"""
Модуль аутентификации и авторизации
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets
import os
import logging
import uuid
import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import redis.asyncio as redis
from fastapi import HTTPException, status
import qrcode
from io import BytesIO
import base64
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database_final import AsyncSessionLocal
from .models.user import User

# Настройка логирования
logger = logging.getLogger("aurion-auth")

# Конфигурация
def _resolve_jwt_secret() -> str:
    """
    Единый источник секрета JWT.
    Приоритет:
    1) JWT_SECRET
    2) AURION_SECRET_KEY (legacy)
    3) безопасный dev fallback
    """
    secret = (
        os.getenv("JWT_SECRET")
        or os.getenv("AURION_SECRET_KEY")
        or "aurion-default-secret-key-change-me"
    )
    return secret


SECRET_KEY = _resolve_jwt_secret()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
FOUNDER_EMAIL = os.getenv("FOUNDER_EMAIL", "martinleterier@mail.ru")
FOUNDER_PASSWORD = os.getenv("FOUNDER_PASSWORD", "71759402")
FOUNDER_USERNAME = os.getenv("FOUNDER_USERNAME", "ceo.martin")

# Redis для refresh токенов
redis_client: Optional[redis.Redis] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля с использованием bcrypt напрямую"""
    # bcrypt имеет ограничение в 72 байта
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """Хеширование пароля с использованием bcrypt напрямую"""
    # bcrypt имеет ограничение в 72 байта
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def generate_totp_secret() -> str:
    """Генерация секрета для TOTP"""
    return secrets.token_hex(20)


def generate_backup_codes(count: int = 10) -> list[str]:
    """Генерация резервных кодов"""
    return [secrets.token_hex(4) for _ in range(count)]


def generate_qr_code(secret: str, email: str) -> str:
    """Генерация QR кода для TOTP"""
    totp_uri = f"otpauth://totp/AurionOS:{email}?secret={secret}&issuer=AurionOS"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание access токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Создание refresh токена (JWT)"""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": user_id, "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def store_refresh_token(user_id: str, refresh_token: str) -> bool:
    """Сохранение refresh токена в Redis (опционально)"""
    if not redis_client:
        return True  # Если Redis нет, полагаемся на JWT валидацию
    
    try:
        await redis_client.setex(
            f"refresh_token:{user_id}",
            REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            refresh_token
        )
        return True
    except Exception as e:
        logger.error(f"Failed to store refresh token in Redis: {e}")
        return False


async def verify_refresh_token(refresh_token: str) -> Optional[str]:
    """Проверка refresh токена и возврат user_id"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        
        user_id: str = payload.get("sub")
        if not user_id:
            return None
            
        # Если есть Redis, проверяем там на отзыв
        if redis_client:
            stored = await redis_client.get(f"refresh_token:{user_id}")
            if not stored or stored.decode() != refresh_token:
                return None
                
        return user_id
    except JWTError:
        return None


async def revoke_refresh_token(user_id: str) -> bool:
    """Отзыв refresh токена"""
    if not redis_client:
        return True
    
    try:
        await redis_client.delete(f"refresh_token:{user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to revoke refresh token: {e}")
        return False


def verify_token(token: str) -> Optional[TokenData]:
    """Проверка access токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
            
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            return None
            
        token_data = TokenData(user_id=user_id, email=email, role=role)
        return token_data
    except JWTError:
        return None


def verify_totp(secret: str, code: str) -> bool:
    """Проверка TOTP кода"""
    import pyotp
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    stmt = select(User).where(
        (User.email == username) | (User.username == username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        is_founder_login = username.lower() == FOUNDER_EMAIL.lower() and password == FOUNDER_PASSWORD
        if not is_founder_login:
            return None

        founder = User(
            email=FOUNDER_EMAIL,
            username=FOUNDER_USERNAME,
            hashed_password=get_password_hash(FOUNDER_PASSWORD),
            display_name="Aurion Creator",
            role="creator",
            is_active=True,
            is_verified=True,
        )
        db.add(founder)
        await db.commit()
        await db.refresh(founder)
        return founder

    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(db: AsyncSession, user_data: Any) -> User:
    """Создание пользователя"""
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        display_name=user_data.display_name or user_data.username,
        is_active=True,
        is_verified=False
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Получение пользователя по ID"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Получение пользователя по email"""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


from .middleware.auth_blacklist import set_redis_client


# Инициализация Redis
async def init_redis():
    """Инициализация Redis клиента"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            logger.info("Redis URL not provided, running in stateless mode")
            return
            
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Redis connected successfully")
        set_redis_client(redis_client)
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        redis_client = None
