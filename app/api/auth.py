"""
API роутер аутентификации
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List

from ..database_final import get_db
get_db_session = get_db


from ..auth import (
    authenticate_user,
    create_user,
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    verify_token,
    verify_refresh_token,
    verify_totp,
    generate_totp_secret,
    generate_backup_codes,
    generate_qr_code,
    verify_password,
    revoke_refresh_token,
    get_user_by_id,
    get_user_by_email,
    SECRET_KEY
)
from ..models.user import User
from ..middleware.auth_blacklist import add_to_blacklist
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
from jose import jwt as jose_jwt

router = APIRouter(tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token", auto_error=False)


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    display_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TOTPSetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]


class TOTPVerify(BaseModel):
    code: str
    otp_token: Optional[str] = None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Получение текущего пользователя"""
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Получение текущего пользователя (опционально, не требует авторизации)"""
    
    if not token:
        return None
    
    try:
        token_data = verify_token(token)
        if not token_data:
            return None
        
        user = await get_user_by_id(db, token_data.user_id)
        return user
    except Exception:
        return None


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Регистрация пользователя"""
    
    # Проверка существующего пользователя
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создание пользователя
    user = await create_user(db, user_data)
    
    # Создание токенов
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(str(user.id))
    
    # Сохранение refresh токена
    await store_refresh_token(str(user.id), refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Вход в систему"""
    
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Создание токенов
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(str(user.id))
    
    # Сохранение refresh токена
    await store_refresh_token(str(user.id), refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=TokenResponse)
async def login_json(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Вход через JSON (основной метод для фронтенда)"""
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(str(user.id))
    await store_refresh_token(str(user.id), refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Обновление access токена"""
    
    # Проверка refresh токена
    user_id = await verify_refresh_token(refresh_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Создание нового access токена
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    # Отзыв старого refresh токена
    await revoke_refresh_token(str(user.id))
    
    # Создание нового refresh токена (rotation)
    new_refresh_token = create_refresh_token(str(user.id))
    await store_refresh_token(str(user.id), new_refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получение информации о текущем пользователе"""
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "two_factor_enabled": current_user.two_factor_enabled,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None
    }


@router.post("/2fa/setup", response_model=TOTPSetupResponse)
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Настройка двухфакторной аутентификации"""
    
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA already enabled"
        )
    
    # Генерация секрета и резервных кодов
    secret = generate_totp_secret()
    backup_codes = generate_backup_codes()
    
    # Генерация QR кода
    qr_code = generate_qr_code(secret, current_user.email)
    
    # Сохранение в базе данных
    current_user.two_factor_secret = secret
    current_user.backup_codes = backup_codes
    await db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes
    }


@router.post("/2fa/enable")
async def enable_2fa(
    data: TOTPVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Включение двухфакторной аутентификации"""
    
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA already enabled"
        )
    
    # Проверка TOTP кода
    if not verify_totp(current_user.two_factor_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Включение 2FA
    current_user.two_factor_enabled = True
    await db.commit()
    
    return {"message": "2FA enabled successfully"}


@router.post("/2fa/disable")
async def disable_2fa(
    password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Отключение двухфакторной аутентификации"""
    
    # Проверка пароля
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )
    
    # Отключение 2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.backup_codes = None
    await db.commit()
    
    return {"message": "2FA disabled successfully"}


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Выход из системы"""
    # Отзыв refresh токена
    await revoke_refresh_token(str(current_user.id))

    # Добавить access token в blacklist
    if token:
        try:
            payload = jose_jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti") or payload.get("sub", "")
            exp = payload.get("exp", 0)
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = max(exp - now, 0)
            if ttl > 0 and jti:
                await add_to_blacklist(jti, ttl)
        except Exception:
            pass

    return {"message": "Logged out successfully"}
