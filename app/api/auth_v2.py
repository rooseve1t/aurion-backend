"""
Auth v2 — регистрация с email-кодом подтверждения и trusted_devices (2FA при входе с нового устройства).
Роутер: /api/v2/auth/
"""
import logging
import random
import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import (
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    get_user_by_email,
)
from ..database_final import get_db
from ..models.user import User
from ..models.payment import Subscription, Tariff
from ..models.trusted_device import TrustedDevice

logger = logging.getLogger("aurion-auth-v2")

router = APIRouter(tags=["auth-v2"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# ---------------------------------------------------------------------------
# Redis helpers (graceful fallback to in-memory when Redis unavailable)
# ---------------------------------------------------------------------------
_memory_store: dict[str, str] = {}
_redis_client: Any = None


def set_redis(client: Any) -> None:
    global _redis_client
    _redis_client = client


async def _redis_set(key: str, value: str, ttl: int) -> None:
    if _redis_client:
        try:
            await _redis_client.setex(key, ttl, value)
            return
        except Exception as exc:
            logger.warning(f"Redis set failed, using memory fallback: {exc}")
    _memory_store[key] = value


async def _redis_get(key: str) -> Optional[str]:
    if _redis_client:
        try:
            val = await _redis_client.get(key)
            return val.decode() if isinstance(val, bytes) else val
        except Exception as exc:
            logger.warning(f"Redis get failed, using memory fallback: {exc}")
    return _memory_store.get(key)


async def _redis_delete(key: str) -> None:
    if _redis_client:
        try:
            await _redis_client.delete(key)
            return
        except Exception as exc:
            logger.warning(f"Redis delete failed: {exc}")
    _memory_store.pop(key, None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_email_code() -> str:
    """Генерация 6-значного кода подтверждения [100000, 999999]."""
    return str(random.randint(100_000, 999_999))


def _device_fingerprint(request: Request) -> str:
    """Fingerprint устройства из User-Agent + IP."""
    ua = request.headers.get("user-agent", "unknown")
    ip = request.client.host if request.client else "unknown"
    return str(hash(ua + ip) % (10 ** 12))


async def _send_email_code(email: str, code: str) -> None:
    """Отправка кода на email через SMTP. Fallback: логирование для разработки."""
    import os
    import smtplib
    from email.mime.text import MIMEText

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    if not smtp_host or not smtp_user:
        logger.warning(f"SMTP не настроен. DEV CODE для {email}: {code}")
        return

    try:
        msg = MIMEText(
            f"Ваш код подтверждения Aurion OS: {code}\n\nКод действителен 15 минут.",
            "plain",
            "utf-8",
        )
        msg["Subject"] = "Код подтверждения Aurion OS"
        msg["From"] = smtp_from
        msg["To"] = email

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [email], msg.as_string())

        logger.info(f"Email code sent to {email}")
    except Exception as exc:
        logger.error(f"Email send failed: {exc}")


async def _ensure_basic_subscription(user: User, db: AsyncSession) -> None:
    """Создать запись Basic-подписки для нового пользователя."""
    try:
        result = await db.execute(select(Tariff).where(Tariff.name == "basic").limit(1))
        tariff = result.scalar_one_or_none()

        if tariff is None:
            tariff = Tariff(
                name="basic",
                display_name="Базовый",
                description="Бесплатный базовый уровень",
                price=0.0,
                billing_interval="month",
                features={"voice": False, "memory_limit": 100},
                is_active=True,
                is_public=True,
            )
            db.add(tariff)
            await db.flush()

        now = datetime.now(timezone.utc)
        subscription = Subscription(
            user_id=user.id,
            tariff_id=tariff.id,
            status="active",
            is_active=True,
            current_period_start=now,
            current_period_end=now + timedelta(days=36500),
            auto_renew=False,
        )
        db.add(subscription)
        await db.flush()
    except Exception as exc:
        logger.warning(f"Could not create basic subscription for user {user.id}: {exc}")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ConfirmDeviceRequest(BaseModel):
    session_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Шаг 1: отправить код подтверждения на email."""
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован.",
        )

    hashed = pwd_context.hash(data.password)
    code = _generate_email_code()

    pending_key = f"pending_registration:{data.email}"
    await _redis_set(
        pending_key,
        json.dumps({
            "hashed_password": hashed,
            "username": data.username or data.email.split("@")[0],
            "code": code,
        }),
        900,
    )

    await _send_email_code(data.email, code)
    return {"message": "Код подтверждения отправлен на email.", "email": data.email}


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Шаг 2: подтвердить email кодом и создать аккаунт."""
    pending_key = f"pending_registration:{data.email}"
    raw = await _redis_get(pending_key)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код истёк или не найден. Запросите новый.",
        )

    pending = json.loads(raw)
    if pending["code"] != data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код подтверждения.",
        )

    user = User(
        email=data.email,
        username=pending["username"],
        hashed_password=pending["hashed_password"],
        is_verified=True,
        is_active=True,
        role="user",
    )
    db.add(user)
    await db.flush()

    await _ensure_basic_subscription(user, db)
    await db.commit()
    await db.refresh(user)
    await _redis_delete(pending_key)

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(str(user.id))
    await store_refresh_token(str(user.id), refresh_token)

    logger.info(f"New user registered: {user.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Вход: bcrypt-проверка + trusted_devices.
    Новое устройство → session_token для 2FA через Telegram.
    """
    result = await db.execute(select(User).where(User.email == data.email).limit(1))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль.",
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Аккаунт деактивирован.")

    fingerprint = _device_fingerprint(request)

    td_result = await db.execute(
        select(TrustedDevice).where(
            TrustedDevice.user_id == user.id,
            TrustedDevice.device_fingerprint == fingerprint,
            TrustedDevice.revoked == False,  # noqa: E712
        ).limit(1)
    )
    trusted = td_result.scalar_one_or_none()

    if trusted:
        trusted.last_seen_at = datetime.now(timezone.utc)
        await db.commit()

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        refresh_token = create_refresh_token(str(user.id))
        await store_refresh_token(str(user.id), refresh_token)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    # Новое устройство — 2FA flow
    session_token = secrets.token_urlsafe(32)
    session_key = f"2fa_session:{session_token}"
    ua = request.headers.get("user-agent", "unknown")
    ip = request.client.host if request.client else "unknown"

    await _redis_set(
        session_key,
        json.dumps({"user_id": str(user.id), "fingerprint": fingerprint, "ua": ua, "ip": ip}),
        600,
    )

    if user.telegram_id:
        try:
            from ..services.telegram_bot import get_bot_instance
            bot = get_bot_instance()
            if bot:
                await bot.send_2fa_request(int(user.telegram_id), f"IP: {ip}, UA: {ua[:60]}", session_token)
        except Exception as exc:
            logger.warning(f"Telegram 2FA notification failed: {exc}")

    return {
        "requires_device_confirmation": True,
        "session_token": session_token,
        "message": "Новое устройство. Подтвердите вход через Telegram.",
    }


@router.post("/confirm-device", response_model=TokenResponse)
async def confirm_device(
    data: ConfirmDeviceRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Подтверждение нового устройства после 2FA. Вызывается Telegram-ботом."""
    session_key = f"2fa_session:{data.session_token}"
    raw = await _redis_get(session_key)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сессия подтверждения истекла или не найдена.",
        )

    session = json.loads(raw)
    user_id = session["user_id"]
    fingerprint = session["fingerprint"]

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")

    td = TrustedDevice(
        user_id=user.id,
        device_fingerprint=fingerprint,
        user_agent=session.get("ua"),
        ip_address=session.get("ip"),
    )
    db.add(td)
    await db.commit()
    await _redis_delete(session_key)

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(str(user.id))
    await store_refresh_token(str(user.id), refresh_token)

    logger.info(f"Device confirmed for user {user.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
