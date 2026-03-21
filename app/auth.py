"""
Модуль аутентификации и авторизации
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets
import hmac
import hashlib
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import redis.asyncio as redis
from fastapi import HTTPException, status
import qrcode
from io import BytesIO
import base64

from .database import AsyncSessionLocal
from .models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

# Конфигурация
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-super-secret-key-change-me-in-production"  # Должно быть в .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

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


class TOTPSetup(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list[str]


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str  # email или username
    password: str


class TOTPVerify(BaseModel):
    code: str
    otp_token: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


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
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Создание refresh токена"""
    refresh_token = secrets.token_urlsafe(32)
    # В реальном приложении здесь сохранение в Redis
    return refresh_token


async def store_refresh_token(user_id: str, refresh_token: str) -> bool:
    """Сохранение refresh токена в Redis"""
    try:
        if redis_client:
            await redis_client.setex(
                f"refresh_token:{user_id}",
                REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
                refresh_token
            )
        return True
    except Exception:
        return False


async def verify_refresh_token(user_id: str, refresh_token: str) -> bool:
    """Проверка refresh токена"""
    try:
        if redis_client:
            stored = await redis_client.get(f"refresh_token:{user_id}")
            return stored and stored.decode() == refresh_token
        return False
    except Exception:
        return False


async def revoke_refresh_token(user_id: str) -> bool:
    """Отзыв refresh токена"""
    try:
        if redis_client:
            await redis_client.delete(f"refresh_token:{user_id}")
        return True
    except Exception:
        return False


def verify_token(token: str) -> Optional[TokenData]:
    """Проверка access токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    # Проверяем по email или username
    from sqlalchemy import select
    
    stmt = select(User).where(
        (User.email == username) | (User.username == username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
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
    from sqlalchemy import select
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Получение пользователя по email"""
    from sqlalchemy import select
    
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def require_role(required_role: str):
    """Декоратор для проверки роли"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Логика проверки роли
            pass
        return wrapper
    return decorator


# Инициализация Redis
async def init_redis():
    """Инициализация Redis клиента"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
    except Exception as e:
        print(f"Redis connection failed: {e}")
        redis_client = None
