from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import socket
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
from urllib.error import URLError
from urllib.parse import parse_qs, quote
from urllib.request import Request as UrlRequest, urlopen
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, Field

APP_STARTED_AT = time.time()
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("AURION_DB_PATH", str(BASE_DIR / "data" / "aurion.db")))
SECRET_KEY = os.getenv("AURION_SECRET_KEY", "aurion-dev-secret-change-me")
ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("AURION_ACCESS_TOKEN_TTL_MINUTES", "60"))
REFRESH_TOKEN_TTL_DAYS = int(os.getenv("AURION_REFRESH_TOKEN_TTL_DAYS", "30"))
TWO_FACTOR_CHALLENGE_TTL_MINUTES = int(os.getenv("AURION_2FA_CHALLENGE_TTL_MINUTES", "10"))
DEMO_EMAIL = "demo@aurionai.ru"
DEMO_PASSWORD = "Demo1234!"
DEMO_USERNAME = "demo"
RUNTIME_CONFIG_FILE = BASE_DIR / "data" / "runtime_config.json"
CREATOR_EMAILS = {
    item.strip().lower()
    for item in os.getenv("AURION_CREATOR_EMAILS", "martinleterier@mail.ru").split(",")
    if item.strip()
}
DEFAULT_VOICE_PERSONA = "calm"
VOICE_PERSONAS = {"calm", "ironic", "sarcastic", "jarvis"}
RUNTIME_CONFIG_KEYS = {
    "QUANTUM_RINGS_TOKEN",
    "YANDEX_FOLDER_ID",
    "YANDEX_API_KEY",
    "CENSYS_API_ID",
    "CENSYS_API_SECRET",
    "SHODAN_API_KEY",
    "APIFY_API_TOKEN",
    "YOOKASSA_SHOP_ID",
    "YOOKASSA_SECRET_KEY",
    "GOOGLE_FIT_CLIENT_ID",
    "GOOGLE_FIT_CLIENT_SECRET",
    "REPLICATE_API_TOKEN",
    "HUGGINGFACE_API_TOKEN",
    "ELEVENLABS_API_KEY",
    "PLANET_API_KEY",
    "REDIS_URL",
    "DATABASE_URL",
    "HPC_UNICORE_URL",
    "HPC_UNICORE_USER",
    "HPC_UNICORE_PASSWORD",
}

DEFAULT_TARIFFS = [
    {
        "name": "Free",
        "price": "0",
        "duration_days": 30,
        "features": {
            "voice": True,
            "memory_limit": 100,
            "devices_limit": 5,
            "osint": False,
            "quantum": False,
            "finance": False,
            "agents": False,
            "evolution": False,
        },
        "is_active": True,
    },
    {
        "name": "Basic",
        "price": "990",
        "duration_days": 30,
        "features": {
            "voice": True,
            "memory_limit": 1000,
            "devices_limit": 20,
            "osint": False,
            "quantum": False,
            "finance": True,
            "agents": False,
            "evolution": False,
        },
        "is_active": True,
    },
    {
        "name": "Pro",
        "price": "2990",
        "duration_days": 30,
        "features": {
            "voice": True,
            "memory_limit": -1,
            "devices_limit": -1,
            "osint": True,
            "quantum": True,
            "finance": True,
            "agents": True,
            "evolution": False,
        },
        "is_active": True,
    },
]

DEFAULT_DEVICE_TEMPLATES = [
    ("Люстра гостиная", "light", "Гостиная", "mqtt", True, {"power": True, "brightness": 78}),
    ("Термостат спальни", "thermostat", "Спальня", "mqtt", True, {"power": True, "temperature": 22}),
    ("Умный замок", "lock", "Прихожая", "matter", True, {"locked": True}),
    ("Датчик движения", "sensor", "Коридор", "zigbee", False, {"motion": False}),
]

DEFAULT_MEMORIES = [
    ("Я предпочитаю спокойный интерфейс без лишнего шума", 8, ["preferences", "ui"]),
    ("По пятницам я обычно разбираю финансы и бытовые задачи", 7, ["habits", "finance"]),
    ("Вечером хочу приглушённый тёплый свет в гостиной", 9, ["smarthome", "comfort"]),
    ("Мне важно видеть короткие и понятные ответы системы", 8, ["ux"]),
]

DEFAULT_AGENTS = [
    ("Финансовый советник", "financial", True, {"focus": "expenses"}),
    ("Домашний координатор", "smarthome", True, {"focus": "comfort"}),
]

DEFAULT_TASKS = [
    ("weekly_review", {"scope": "expenses"}, "completed", {"summary": "Расходы стабильны, лучшее окно для экономии — подписки."}),
    ("gentle_morning", {"room": "Гостиная"}, "queued", {"note": "Сценарий мягкого утра готов к запуску."}),
]

DEFAULT_ACCOUNTS = [
    ("Т-Банк", "debit", "86420.15", "RUB", "**** 4821"),
    ("Альфа", "savings", "215000.00", "RUB", "**** 9954"),
]

DEFAULT_TRANSACTIONS = [
    (-1890.0, "Подписки", "Продление рабочих сервисов"),
    (-1240.0, "Дом", "Лампы и датчики для умного дома"),
    (-890.0, "Еда", "Заказ продуктов"),
    (-3200.0, "Транспорт", "Такси и каршеринг"),
    (95000.0, "Доход", "Основной доход"),
]


class RegisterData(BaseModel):
    email: str
    username: str
    password: str = Field(min_length=8)


class RefreshRequest(BaseModel):
    refresh_token: str


class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)
    otp_token: str


class TwoFactorCodeRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class MemoryCreateRequest(BaseModel):
    content: str
    importance: int = Field(default=5, ge=1, le=10)
    tags: list[str] = Field(default_factory=list)


class DeviceCreateRequest(BaseModel):
    name: str
    device_type: str
    room: str
    protocol: str = "mqtt"


class DeviceControlRequest(BaseModel):
    device_id: Union[int, str]
    command: str
    params: dict[str, Any] = Field(default_factory=dict)


class AgentCreateRequest(BaseModel):
    name: str
    agent_type: str
    config: dict[str, Any] = Field(default_factory=dict)


class TaskCreateRequest(BaseModel):
    agent_id: int
    action: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class SwarmRequest(BaseModel):
    goal: str


class SubscribeRequest(BaseModel):
    tariff_id: int
    save_payment_method: bool = True


class VoicePreferencesUpdateRequest(BaseModel):
    persona: str = Field(default=DEFAULT_VOICE_PERSONA)


class ProactiveGenerateRequest(BaseModel):
    lookback_days: int = Field(default=30, ge=7, le=180)


class VoiceProfileEnrollRequest(BaseModel):
    profile_name: str = Field(min_length=2, max_length=64)
    audio_sample_b64: str = Field(min_length=20)


class VoiceIdentifyRequest(BaseModel):
    audio_sample_b64: str = Field(min_length=20)


class DIYSketchUploadRequest(BaseModel):
    name: str
    device_type: str
    board: str = "ESP8266"
    sketch_code: str = Field(min_length=10)
    protocol: str = "mqtt"


class QuantumRouteRequest(BaseModel):
    task_type: str = "optimization"
    payload: dict[str, Any] = Field(default_factory=dict)
    preferred_backend: str = "auto"


class GuardianScanRequest(BaseModel):
    hosts: list[str] = Field(default_factory=lambda: ["192.168.1.1", "192.168.1.100"])
    ports: list[int] = Field(default_factory=lambda: [22, 80, 443, 1883, 3306, 5432])
    timeout_seconds: float = Field(default=0.2, ge=0.05, le=2.0)


class ConfigUpdateRequest(BaseModel):
    updates: dict[str, str] = Field(default_factory=dict)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return to_iso(utc_now())


def to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def from_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_parent_dir(DB_PATH)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def role_for_email(email: str) -> str:
    return "creator" if email.strip().lower() in CREATOR_EMAILS else "user"


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def json_loads(value: Optional[str], default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)


def load_runtime_config() -> dict[str, str]:
    config: dict[str, str] = {}
    for key in RUNTIME_CONFIG_KEYS:
        value = os.getenv(key, "").strip()
        if value:
            config[key] = value
    if RUNTIME_CONFIG_FILE.exists():
        try:
            raw = json.loads(RUNTIME_CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for key, value in raw.items():
                    if key in RUNTIME_CONFIG_KEYS and isinstance(value, str) and value.strip():
                        config[key] = value.strip()
        except (OSError, json.JSONDecodeError):
            pass
    return config


def save_runtime_config(config: dict[str, str]) -> None:
    ensure_parent_dir(RUNTIME_CONFIG_FILE)
    RUNTIME_CONFIG_FILE.write_text(
        json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


RUNTIME_CONFIG: dict[str, str] = load_runtime_config()


def config_get(key: str, default: str = "") -> str:
    return (RUNTIME_CONFIG.get(key) or os.getenv(key) or default).strip()


def mask_secret(value: str) -> str:
    if len(value) <= 6:
        return "*" * len(value)
    return f"{value[:3]}***{value[-3:]}"


def infer_emotion(content: str, persona: str) -> str:
    lowered = content.lower()
    if persona in {"ironic", "sarcastic"}:
        return persona
    if any(token in lowered for token in ["срочно", "тревога", "ошибка", "panic"]):
        return "calm"
    if any(token in lowered for token in ["лол", "шут", "ирони", "сарказ"]):
        return "ironic"
    return "calm"


def voice_fingerprint(audio_sample_b64: str) -> str:
    raw = audio_sample_b64.strip().encode("utf-8")
    normalized = re.sub(rb"[^a-zA-Z0-9+/=]", b"", raw)
    return hashlib.sha256(normalized).hexdigest()


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def b64url_decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    real_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), real_salt.encode("utf-8"), 240000)
    return real_salt, digest.hex()


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    _, digest = hash_password(password, salt)
    return hmac.compare_digest(digest, password_hash)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user_id: str, email: str) -> str:
    header = b64url_encode(json_dumps({"alg": "HS256", "typ": "AURION"}).encode("utf-8"))
    payload = b64url_encode(
        json_dumps(
            {
                "sub": user_id,
                "email": email,
                "exp": int(time.time()) + ACCESS_TOKEN_TTL_MINUTES * 60,
            }
        ).encode("utf-8")
    )
    signing_input = f"{header}.{payload}".encode("utf-8")
    signature = b64url_encode(hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        header_b64, payload_b64, signature = token.split(".")
    except ValueError:
        return None

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_signature = b64url_encode(hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        payload = json.loads(b64url_decode(payload_b64))
    except (json.JSONDecodeError, ValueError):
        return None

    if int(payload.get("exp", 0)) <= int(time.time()):
        return None
    return payload


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def generate_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("utf-8").rstrip("=")


def normalize_totp_secret(secret: str) -> bytes:
    padding = "=" * (-len(secret) % 8)
    return base64.b32decode(secret + padding, casefold=True)


def generate_totp(secret: str, for_time: Optional[int] = None, interval: int = 30) -> str:
    counter = int((for_time or int(time.time())) // interval)
    key = normalize_totp_secret(secret)
    msg = counter.to_bytes(8, "big")
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = int.from_bytes(digest[offset:offset + 4], "big") & 0x7FFFFFFF
    return str(binary % 1_000_000).zfill(6)


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    now = int(time.time())
    sanitized = code.strip()
    for offset in range(-window, window + 1):
        if hmac.compare_digest(generate_totp(secret, now + offset * 30), sanitized):
            return True
    return False


def make_qr_data_url(payload: str) -> str:
    try:
        import qrcode
    except ImportError:
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240' viewBox='0 0 240 240'>"
            "<rect width='240' height='240' fill='#081015' rx='16'/>"
            "<text x='120' y='112' fill='#e2f7ff' text-anchor='middle' font-family='monospace' font-size='12'>"
            "Сканируйте otpauth URL"
            "</text>"
            "<text x='120' y='136' fill='#6ac9ff' text-anchor='middle' font-family='monospace' font-size='10'>"
            "или используйте секрет вручную"
            "</text>"
            "</svg>"
        )
        return f"data:image/svg+xml;utf8,{quote(svg)}"

    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    try:
        image.save(buffer, format="PNG")
    except TypeError:
        image.save(buffer)
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"


def serialize_user(row: sqlite3.Row) -> dict[str, Any]:
    is_2fa_enabled = bool(row["is_2fa_enabled"])
    return {
        "id": row["id"],
        "email": row["email"],
        "username": row["username"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "is_2fa_enabled": is_2fa_enabled,
        "two_factor_enabled": is_2fa_enabled,
        "created_at": row["created_at"],
    }


def serialize_memory(row: sqlite3.Row, similarity: Optional[float] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "id": row["id"],
        "content": row["content"],
        "importance": row["importance"],
        "tags": json_loads(row["tags"], []),
        "created_at": row["created_at"],
    }
    if similarity is not None:
        payload["similarity"] = round(similarity, 3)
    return payload


def serialize_device(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "device_type": row["device_type"],
        "type": row["device_type"],
        "room": row["room"],
        "protocol": row["protocol"],
        "is_online": bool(row["is_online"]),
        "state": json_loads(row["state"], {}),
        "created_at": row["created_at"],
    }


def serialize_agent(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "agent_type": row["agent_type"],
        "type": row["agent_type"],
        "description": f"Автономный агент типа {row['agent_type']}",
        "config": json_loads(row["config"], {}),
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
    }


def serialize_task(row: sqlite3.Row) -> dict[str, Any]:
    parameters = json_loads(row["parameters"], {})
    result = json_loads(row["result"], None)
    return {
        "id": row["id"],
        "agent_id": row["agent_id"],
        "action": row["action"],
        "type": row["action"],
        "parameters": parameters,
        "input_data": parameters,
        "status": row["status"],
        "result": result,
        "output_data": result,
        "error_message": row["error_message"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def serialize_tariff(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "price": row["price"],
        "duration_days": row["duration_days"],
        "features": json_loads(row["features"], {}),
        "is_active": bool(row["is_active"]),
    }


def serialize_subscription(row: sqlite3.Row, tariff: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    end_date = from_iso(row["end_date"])
    days_left = None
    if end_date:
        days_left = max((end_date - utc_now()).days, 0)
    return {
        "id": row["id"],
        "tariff_id": row["tariff_id"],
        "status": row["status"],
        "start_date": row["start_date"],
        "end_date": row["end_date"],
        "auto_renew": bool(row["auto_renew"]),
        "cancelled_at": row["cancelled_at"],
        "created_at": row["created_at"],
        "tariff": tariff,
        "days_left": days_left,
    }


def serialize_payment(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "subscription_id": row["subscription_id"],
        "amount": row["amount"],
        "currency": row["currency"],
        "status": row["status"],
        "description": row["description"],
        "created_at": row["created_at"],
    }


def serialize_account(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "bank_name": row["bank_name"],
        "account_type": row["account_type"],
        "balance": row["balance"],
        "currency": row["currency"],
        "account_number": row["account_number"],
    }


def serialize_transaction(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "amount": row["amount"],
        "category": row["category"],
        "description": row["description"],
        "date": row["date"],
        "type": row["type"],
    }


def create_schema() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1,
                is_2fa_enabled INTEGER NOT NULL DEFAULT 0,
                two_factor_secret TEXT,
                two_factor_pending INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                revoked_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS login_challenges (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS memory_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                importance INTEGER NOT NULL,
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                room TEXT NOT NULL,
                protocol TEXT NOT NULL,
                is_online INTEGER NOT NULL DEFAULT 1,
                state TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                config TEXT NOT NULL DEFAULT '{}',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS agent_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                agent_id INTEGER,
                action TEXT NOT NULL,
                parameters TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL,
                result TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(agent_id) REFERENCES agents(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS tariffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                features TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                tariff_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                auto_renew INTEGER NOT NULL DEFAULT 0,
                cancelled_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(tariff_id) REFERENCES tariffs(id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                subscription_id INTEGER,
                amount TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'RUB',
                status TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS finance_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                bank_name TEXT NOT NULL,
                account_type TEXT NOT NULL,
                balance TEXT NOT NULL,
                currency TEXT NOT NULL,
                account_number TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                account_id INTEGER NOT NULL,
                amount TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(account_id) REFERENCES finance_accounts(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                voice_persona TEXT NOT NULL DEFAULT 'calm',
                proactive_enabled INTEGER NOT NULL DEFAULT 1,
                family_mode INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS voice_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                profile_name TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                provider TEXT NOT NULL DEFAULT 'mvp-hash',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS proactive_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 0.5,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS diy_sketches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                board TEXT NOT NULL,
                protocol TEXT NOT NULL,
                sketch_code TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()


def get_tariff_by_name(conn: sqlite3.Connection, name: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM tariffs WHERE name = ?", (name,)).fetchone()


def get_tariff_by_id(conn: sqlite3.Connection, tariff_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM tariffs WHERE id = ?", (tariff_id,)).fetchone()


def seed_reference_data(conn: sqlite3.Connection) -> None:
    for tariff in DEFAULT_TARIFFS:
        existing = get_tariff_by_name(conn, tariff["name"])
        if existing:
            conn.execute(
                """
                UPDATE tariffs
                SET price = ?, duration_days = ?, features = ?, is_active = ?
                WHERE id = ?
                """,
                (
                    tariff["price"],
                    tariff["duration_days"],
                    json_dumps(tariff["features"]),
                    int(tariff["is_active"]),
                    existing["id"],
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO tariffs (name, price, duration_days, features, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    tariff["name"],
                    tariff["price"],
                    tariff["duration_days"],
                    json_dumps(tariff["features"]),
                    int(tariff["is_active"]),
                ),
            )
    conn.commit()


def ensure_creator_roles(conn: sqlite3.Connection) -> None:
    if not CREATOR_EMAILS:
        return
    placeholders = ", ".join("?" for _ in CREATOR_EMAILS)
    conn.execute(
        f"UPDATE users SET role = 'creator' WHERE lower(email) IN ({placeholders})",
        tuple(sorted(CREATOR_EMAILS)),
    )
    conn.commit()


def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()


def get_user_by_id(conn: sqlite3.Connection, user_id: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM users WHERE lower(username) = lower(?)", (username,)).fetchone()


def get_current_subscription_row(conn: sqlite3.Connection, user_id: str) -> Optional[sqlite3.Row]:
    row = conn.execute(
        """
        SELECT *
        FROM subscriptions
        WHERE user_id = ?
        ORDER BY
            CASE status
                WHEN 'active' THEN 0
                WHEN 'pending' THEN 1
                WHEN 'cancelled' THEN 2
                ELSE 3
            END,
            datetime(created_at) DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    if not row:
        return None
    end_date = from_iso(row["end_date"])
    if row["status"] == "active" and end_date and end_date < utc_now():
        conn.execute("UPDATE subscriptions SET status = 'expired' WHERE id = ?", (row["id"],))
        conn.commit()
        return conn.execute("SELECT * FROM subscriptions WHERE id = ?", (row["id"],)).fetchone()
    return row


def ensure_free_subscription(conn: sqlite3.Connection, user_id: str) -> None:
    existing = get_current_subscription_row(conn, user_id)
    if existing:
        return
    free_tariff = get_tariff_by_name(conn, "Free")
    if not free_tariff:
        raise RuntimeError("Free tariff is missing")
    now = utc_now()
    conn.execute(
        """
        INSERT INTO subscriptions (user_id, tariff_id, status, start_date, end_date, auto_renew, cancelled_at, created_at)
        VALUES (?, ?, 'active', ?, ?, 1, NULL, ?)
        """,
        (user_id, free_tariff["id"], to_iso(now), to_iso(now + timedelta(days=free_tariff["duration_days"])), to_iso(now)),
    )
    conn.commit()


def ensure_seeded_workspace(conn: sqlite3.Connection, user_id: str) -> None:
    ensure_free_subscription(conn, user_id)
    pref_row = conn.execute(
        "SELECT user_id FROM user_preferences WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if not pref_row:
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, voice_persona, proactive_enabled, family_mode, updated_at)
            VALUES (?, ?, 1, 1, ?)
            """,
            (user_id, DEFAULT_VOICE_PERSONA, iso_now()),
        )

    device_count = conn.execute("SELECT COUNT(*) FROM devices WHERE user_id = ?", (user_id,)).fetchone()[0]
    if device_count == 0:
        for name, device_type, room, protocol, is_online, state in DEFAULT_DEVICE_TEMPLATES:
            conn.execute(
                """
                INSERT INTO devices (user_id, name, device_type, room, protocol, is_online, state, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, name, device_type, room, protocol, int(is_online), json_dumps(state), iso_now()),
            )

    memory_count = conn.execute("SELECT COUNT(*) FROM memory_entries WHERE user_id = ?", (user_id,)).fetchone()[0]
    if memory_count == 0:
        for content, importance, tags in DEFAULT_MEMORIES:
            conn.execute(
                """
                INSERT INTO memory_entries (user_id, content, importance, tags, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, content, importance, json_dumps(tags), iso_now()),
            )

    agent_count = conn.execute("SELECT COUNT(*) FROM agents WHERE user_id = ?", (user_id,)).fetchone()[0]
    if agent_count == 0:
        for name, agent_type, is_active, config in DEFAULT_AGENTS:
            conn.execute(
                """
                INSERT INTO agents (user_id, name, agent_type, config, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, name, agent_type, json_dumps(config), int(is_active), iso_now()),
            )

    account_count = conn.execute("SELECT COUNT(*) FROM finance_accounts WHERE user_id = ?", (user_id,)).fetchone()[0]
    if account_count == 0:
        for bank_name, account_type, balance, currency, account_number in DEFAULT_ACCOUNTS:
            conn.execute(
                """
                INSERT INTO finance_accounts (user_id, bank_name, account_type, balance, currency, account_number)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, bank_name, account_type, balance, currency, account_number),
            )

    account_row = conn.execute(
        "SELECT id FROM finance_accounts WHERE user_id = ? ORDER BY id ASC LIMIT 1",
        (user_id,),
    ).fetchone()
    transaction_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (user_id,)).fetchone()[0]
    if account_row and transaction_count == 0:
        now = utc_now()
        for index, (amount, category, description) in enumerate(DEFAULT_TRANSACTIONS):
            tx_time = now - timedelta(days=index * 3)
            conn.execute(
                """
                INSERT INTO transactions (user_id, account_id, amount, category, description, date, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    account_row["id"],
                    f"{amount:.2f}",
                    category,
                    description,
                    to_iso(tx_time),
                    "credit" if amount > 0 else "debit",
                ),
            )

    task_count = conn.execute("SELECT COUNT(*) FROM agent_tasks WHERE user_id = ?", (user_id,)).fetchone()[0]
    if task_count == 0:
        first_agent = conn.execute("SELECT id FROM agents WHERE user_id = ? ORDER BY id ASC LIMIT 1", (user_id,)).fetchone()
        if first_agent:
            for action, parameters, status, result in DEFAULT_TASKS:
                conn.execute(
                    """
                    INSERT INTO agent_tasks (user_id, agent_id, action, parameters, status, result, error_message, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)
                    """,
                    (
                        user_id,
                        first_agent["id"],
                        action,
                        json_dumps(parameters),
                        status,
                        json_dumps(result),
                        iso_now(),
                        iso_now(),
                    ),
                )

    conn.commit()


def seed_demo_user(conn: sqlite3.Connection) -> None:
    existing = get_user_by_email(conn, DEMO_EMAIL)
    if existing:
        ensure_seeded_workspace(conn, existing["id"])
        return

    user_id = str(uuid4())
    salt, password_hash = hash_password(DEMO_PASSWORD)
    conn.execute(
        """
        INSERT INTO users (
            id, email, username, password_hash, password_salt, role,
            is_active, is_2fa_enabled, two_factor_secret, two_factor_pending, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, 1, 0, NULL, 0, ?)
        """,
        (user_id, DEMO_EMAIL, DEMO_USERNAME, password_hash, salt, role_for_email(DEMO_EMAIL), iso_now()),
    )
    conn.commit()
    ensure_seeded_workspace(conn, user_id)


def bootstrap() -> None:
    create_schema()
    with get_connection() as conn:
        seed_reference_data(conn)
        seed_demo_user(conn)
        ensure_creator_roles(conn)


def create_auth_pair(conn: sqlite3.Connection, user_row: sqlite3.Row) -> dict[str, str]:
    refresh_token = generate_refresh_token()
    refresh_expires_at = utc_now() + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
    conn.execute(
        """
        INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at, created_at, revoked_at)
        VALUES (?, ?, ?, ?, ?, NULL)
        """,
        (str(uuid4()), user_row["id"], hash_refresh_token(refresh_token), to_iso(refresh_expires_at), iso_now()),
    )
    conn.commit()
    return {
        "access_token": create_access_token(user_row["id"], user_row["email"]),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def revoke_refresh_token(conn: sqlite3.Connection, refresh_token: str) -> None:
    conn.execute(
        "UPDATE refresh_tokens SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL",
        (iso_now(), hash_refresh_token(refresh_token)),
    )
    conn.commit()


def get_current_user(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    payload = decode_access_token(authorization.split(" ", 1)[1].strip())
    if not payload:
        raise HTTPException(status_code=401, detail="Токен недействителен или истёк")

    with get_connection() as conn:
        user_row = get_user_by_id(conn, payload["sub"])
        if not user_row or not bool(user_row["is_active"]):
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        ensure_seeded_workspace(conn, user_row["id"])
        return serialize_user(user_row)


def get_user_row_or_404(conn: sqlite3.Connection, user_id: str) -> sqlite3.Row:
    row = get_user_by_id(conn, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return row


def build_subscription_payload(conn: sqlite3.Connection, row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    tariff_row = get_tariff_by_id(conn, row["tariff_id"])
    tariff = serialize_tariff(tariff_row) if tariff_row else None
    return serialize_subscription(row, tariff)


def search_memory_score(content: str, query: str) -> float:
    if not query.strip():
        return 1.0
    query_words = {item for item in query.lower().split() if item}
    content_words = {item.strip(".,!?").lower() for item in content.split() if item}
    if not query_words:
        return 1.0
    overlap = len(query_words & content_words)
    substring_bonus = 1 if query.lower() in content.lower() else 0
    return min(1.0, (overlap + substring_bonus) / max(len(query_words), 1))


def build_task_result(action: str, parameters: dict[str, Any]) -> dict[str, Any]:
    if action in {"weekly_review", "analyze_spending"}:
        return {
            "summary": "Основной рост расходов — транспорт и подписки. Хороший потенциал экономии на повторяющихся тратах.",
            "tips": ["Сверить автосписания", "Сократить спонтанные поездки на такси"],
        }
    if action in {"gentle_morning", "optimize_home"}:
        return {
            "summary": "Сценарий мягкого утра активирован: тёплый свет, комфортная температура и постепенное пробуждение.",
            "actions": ["Включить тёплый свет", "Прогреть спальню до 22°C"],
        }
    if action in {"search_ip", "search_email"}:
        return {
            "summary": "OSINT-поиск завершён. Найдены публичные упоминания и связанный цифровой след.",
            "matches": 4,
        }
    if action in {"memory_summary", "recall_memory"}:
        return {
            "summary": "В памяти преобладают бытовые привычки, настройки комфорта и личные предпочтения пользователя.",
        }
    if action == "swarm":
        return {
            "summary": "Рой агентов разложил цель на несколько параллельных направлений и подготовил план действий.",
            "goal": parameters.get("goal"),
        }
    return {
        "summary": "Задача выполнена в MVP-режиме.",
        "parameters": parameters,
    }


def build_chat_reply(conn: sqlite3.Connection, user_id: str, message: str) -> str:
    lowered = message.lower()
    memory_count = conn.execute("SELECT COUNT(*) FROM memory_entries WHERE user_id = ?", (user_id,)).fetchone()[0]
    online_devices = conn.execute(
        "SELECT COUNT(*) FROM devices WHERE user_id = ? AND is_online = 1",
        (user_id,),
    ).fetchone()[0]
    active_tasks = conn.execute(
        "SELECT COUNT(*) FROM agent_tasks WHERE user_id = ? AND status IN ('queued', 'running')",
        (user_id,),
    ).fetchone()[0]

    if any(keyword in lowered for keyword in ["статус", "система", "system"]):
        return (
            f"Система в норме: устройств онлайн — {online_devices}, "
            f"записей памяти — {memory_count}, активных задач — {active_tasks}."
        )
    if any(keyword in lowered for keyword in ["дом", "свет", "термостат", "замок"]):
        device_rows = conn.execute(
            "SELECT name, state FROM devices WHERE user_id = ? ORDER BY id ASC LIMIT 3",
            (user_id,),
        ).fetchall()
        snippets = []
        for row in device_rows:
            state = json_loads(row["state"], {})
            if "power" in state:
                snippets.append(f"{row['name']}: {'включено' if state['power'] else 'выключено'}")
            elif "temperature" in state:
                snippets.append(f"{row['name']}: {state['temperature']}°C")
            elif "locked" in state:
                snippets.append(f"{row['name']}: {'закрыт' if state['locked'] else 'открыт'}")
        return "Умный дом готов. " + "; ".join(snippets or ["ключевые устройства пока не найдены"])
    if any(keyword in lowered for keyword in ["задач", "агент", "рой"]):
        return f"Сейчас у вас {active_tasks} активных задач агентов. Могу помочь сформулировать новую цель для автоматизации."
    if any(keyword in lowered for keyword in ["памят", "запомни", "история"]):
        recent = conn.execute(
            "SELECT content FROM memory_entries WHERE user_id = ? ORDER BY id DESC LIMIT 2",
            (user_id,),
        ).fetchall()
        if recent:
            return "В памяти уже есть свежие записи: " + " | ".join(row["content"] for row in recent)
        return "Память пока пуста, но я готов сохранять важные заметки."
    return (
        "Я уже работаю как живой MVP: умею хранить память, показывать статус дома, "
        "вести базовые задачи агентов и обслуживать регистрацию с 2FA."
    )


def get_user_preferences(conn: sqlite3.Connection, user_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if not row:
        ensure_seeded_workspace(conn, user_id)
        row = conn.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return {
        "voice_persona": row["voice_persona"] if row else DEFAULT_VOICE_PERSONA,
        "proactive_enabled": bool(row["proactive_enabled"]) if row else True,
        "family_mode": bool(row["family_mode"]) if row else True,
    }


def update_user_preferences(conn: sqlite3.Connection, user_id: str, voice_persona: str) -> dict[str, Any]:
    persona = voice_persona.strip().lower()
    if persona not in VOICE_PERSONAS:
        raise HTTPException(status_code=400, detail=f"Недопустимая персона. Доступно: {sorted(VOICE_PERSONAS)}")
    conn.execute(
        """
        INSERT INTO user_preferences (user_id, voice_persona, proactive_enabled, family_mode, updated_at)
        VALUES (?, ?, 1, 1, ?)
        ON CONFLICT(user_id) DO UPDATE SET voice_persona = excluded.voice_persona, updated_at = excluded.updated_at
        """,
        (user_id, persona, iso_now()),
    )
    conn.commit()
    return get_user_preferences(conn, user_id)


def generate_proactive_suggestions(conn: sqlite3.Connection, user_id: str, lookback_days: int = 30) -> list[dict[str, Any]]:
    since = to_iso(utc_now() - timedelta(days=lookback_days))
    memory_rows = conn.execute(
        """
        SELECT content, tags
        FROM memory_entries
        WHERE user_id = ? AND datetime(created_at) >= datetime(?)
        ORDER BY importance DESC, datetime(created_at) DESC
        """,
        (user_id, since),
    ).fetchall()
    task_rows = conn.execute(
        """
        SELECT action, parameters, created_at
        FROM agent_tasks
        WHERE user_id = ? AND datetime(created_at) >= datetime(?)
        ORDER BY datetime(created_at) DESC
        """,
        (user_id, since),
    ).fetchall()

    suggestions: list[tuple[str, float, str]] = []
    joined_memory = " ".join((row["content"] or "").lower() for row in memory_rows)
    weekday = datetime.now().weekday()
    if weekday == 4 and any(token in joined_memory for token in ["пятниц", "pizza", "пицц"]):
        suggestions.append(("Вы обычно заказываете пиццу по пятницам. Повторить заказ?", 0.86, "habit:friday_pizza"))
    if any(token in joined_memory for token in ["финанс", "бюджет", "расход"]):
        suggestions.append(("Пятничный финобзор готов. Запустить короткий анализ расходов?", 0.81, "habit:finance_review"))
    if any(row["action"] in {"weekly_review", "analyze_spending"} for row in task_rows):
        suggestions.append(("Обнаружен стабильный финансовый ритм. Включить авто-еженедельный отчёт?", 0.77, "agent:recurring_task"))
    if any(token in joined_memory for token in ["свет", "гостиная", "вечер"]):
        suggestions.append(("Вечерний сценарий света можно запускать автоматически в 21:00. Включить?", 0.73, "smarthome:evening_scene"))
    if not suggestions:
        suggestions.append(("Пока мало данных для уверенной проактивности. Сохраняйте заметки в Память для персонализации.", 0.4, "cold_start"))

    payload: list[dict[str, Any]] = []
    for message, confidence, source in suggestions[:5]:
        conn.execute(
            """
            INSERT INTO proactive_suggestions (user_id, message, confidence, source, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, message, confidence, source, iso_now()),
        )
        payload.append({"message": message, "confidence": round(confidence, 2), "source": source})
    conn.commit()
    return payload


def synthesize_tts(text: str, emotion: str, persona: str) -> dict[str, Any]:
    api_key = config_get("YANDEX_API_KEY")
    folder_id = config_get("YANDEX_FOLDER_ID")
    if not api_key or not folder_id:
        return {
            "provider": "mvp-fallback",
            "audio_b64": "",
            "emotion": emotion,
            "persona": persona,
            "note": "YANDEX_API_KEY / YANDEX_FOLDER_ID не заданы",
        }

    payload = json.dumps(
        {
            "text": text,
            "lang": "ru-RU",
            "voice": "jane",
            "folderId": folder_id,
            "format": "lpcm",
            "sampleRateHertz": 48000,
            "emotion": "good" if emotion in {"calm", "ironic"} else "evil",
        }
    ).encode("utf-8")
    req = UrlRequest(
        "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize",
        data=payload,
        headers={
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=8) as response:
            audio = response.read()
        return {
            "provider": "yandex-speechkit",
            "audio_b64": base64.b64encode(audio).decode("utf-8"),
            "emotion": emotion,
            "persona": persona,
        }
    except (URLError, TimeoutError, ValueError):
        return {
            "provider": "mvp-fallback",
            "audio_b64": "",
            "emotion": emotion,
            "persona": persona,
            "note": "Yandex SpeechKit временно недоступен",
        }


def scan_host_ports(host: str, ports: list[int], timeout_seconds: float) -> list[int]:
    open_ports: list[int] = []
    for port in ports[:32]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_seconds)
        try:
            if sock.connect_ex((host, port)) == 0:
                open_ports.append(port)
        except OSError:
            pass
        finally:
            sock.close()
    return open_ports


def check_redis_connection() -> dict[str, Any]:
    redis_url = config_get("REDIS_URL")
    if not redis_url:
        return {"enabled": False, "status": "not_configured"}
    try:
        import redis

        client = redis.Redis.from_url(redis_url, socket_timeout=1.5)
        pong = client.ping()
        return {"enabled": True, "status": "ok" if pong else "error"}
    except Exception as exc:
        return {"enabled": True, "status": "error", "error": str(exc)}


def check_postgres_connection() -> dict[str, Any]:
    database_url = config_get("DATABASE_URL")
    if not database_url:
        return {"enabled": False, "status": "not_configured"}
    try:
        import psycopg

        with psycopg.connect(database_url, connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                _ = cur.fetchone()
        return {"enabled": True, "status": "ok"}
    except Exception as exc:
        return {"enabled": True, "status": "error", "error": str(exc)}


async def parse_request_payload(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            return await request.json()
        except json.JSONDecodeError:
            return {}
    raw_body = (await request.body()).decode("utf-8")
    parsed = parse_qs(raw_body)
    return {key: values[0] for key, values in parsed.items()}


bootstrap()

app = FastAPI(title="Aurion OS MVP", version="2.0.0")

raw_allowed_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
allowed_origins = [item.strip() for item in raw_allowed_origins.split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": "2.0.0",
        "database": str(DB_PATH),
        "uptime_seconds": int(time.time() - APP_STARTED_AT),
    }


@app.post("/api/v1/auth/register")
async def register(data: RegisterData) -> dict[str, Any]:
    email = data.email.strip().lower()
    username = data.username.strip()
    if not email or not username:
        raise HTTPException(status_code=400, detail="Email и username обязательны")

    with get_connection() as conn:
        if get_user_by_email(conn, email):
            raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
        if get_user_by_username(conn, username):
            raise HTTPException(status_code=409, detail="Имя пользователя уже занято")

        user_id = str(uuid4())
        salt, password_hash = hash_password(data.password)
        conn.execute(
            """
            INSERT INTO users (
                id, email, username, password_hash, password_salt, role,
                is_active, is_2fa_enabled, two_factor_secret, two_factor_pending, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 1, 0, NULL, 0, ?)
            """,
            (user_id, email, username, password_hash, salt, role_for_email(email), iso_now()),
        )
        conn.commit()
        ensure_seeded_workspace(conn, user_id)
        user_row = get_user_by_id(conn, user_id)
        return serialize_user(user_row)


@app.post("/api/v1/auth/token")
async def login(request: Request) -> JSONResponse:
    payload = await parse_request_payload(request)
    email = (payload.get("username") or payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()
    if not email or not password:
        raise HTTPException(status_code=422, detail="Нужны email/username и password")

    with get_connection() as conn:
        user_row = get_user_by_email(conn, email)
        if not user_row or not verify_password(password, user_row["password_salt"], user_row["password_hash"]):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

        if bool(user_row["is_2fa_enabled"]):
            challenge_id = str(uuid4())
            conn.execute(
                """
                INSERT INTO login_challenges (id, user_id, expires_at, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    challenge_id,
                    user_row["id"],
                    to_iso(utc_now() + timedelta(minutes=TWO_FACTOR_CHALLENGE_TTL_MINUTES)),
                    iso_now(),
                ),
            )
            conn.commit()
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "2FA required",
                    "requires_2fa": True,
                    "otp_token": challenge_id,
                },
            )

        ensure_seeded_workspace(conn, user_row["id"])
        return JSONResponse(content=create_auth_pair(conn, user_row))


@app.post("/api/v1/auth/refresh")
async def refresh_tokens(data: RefreshRequest) -> dict[str, str]:
    token_hash = hash_refresh_token(data.refresh_token)
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM refresh_tokens
            WHERE token_hash = ? AND revoked_at IS NULL
            ORDER BY datetime(created_at) DESC
            LIMIT 1
            """,
            (token_hash,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Refresh token недействителен")

        expires_at = from_iso(row["expires_at"])
        if not expires_at or expires_at <= utc_now():
            revoke_refresh_token(conn, data.refresh_token)
            raise HTTPException(status_code=401, detail="Refresh token истёк")

        user_row = get_user_by_id(conn, row["user_id"])
        if not user_row:
            revoke_refresh_token(conn, data.refresh_token)
            raise HTTPException(status_code=401, detail="Пользователь не найден")

        revoke_refresh_token(conn, data.refresh_token)
        return create_auth_pair(conn, user_row)


@app.post("/api/v1/auth/logout")
async def logout(data: RefreshRequest, current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, bool]:
    with get_connection() as conn:
        revoke_refresh_token(conn, data.refresh_token)
    return {"ok": True}


@app.get("/api/v1/auth/me")
async def me(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return current_user


@app.post("/api/v1/auth/2fa/enable")
async def enable_2fa(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    with get_connection() as conn:
        user_row = get_user_row_or_404(conn, current_user["id"])
        secret = user_row["two_factor_secret"] or generate_totp_secret()
        conn.execute(
            """
            UPDATE users
            SET two_factor_secret = ?, two_factor_pending = 1
            WHERE id = ?
            """,
            (secret, user_row["id"]),
        )
        conn.commit()
        otpauth_url = (
            f"otpauth://totp/Aurion:{quote(user_row['email'])}"
            f"?secret={secret}&issuer=Aurion&algorithm=SHA1&digits=6&period=30"
        )
        return {
            "secret": secret,
            "otpauth_url": otpauth_url,
            "qr_code": make_qr_data_url(otpauth_url),
        }


@app.post("/api/v1/auth/2fa/verify-enable")
async def verify_enable_2fa(
    data: TwoFactorCodeRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, bool]:
    with get_connection() as conn:
        user_row = get_user_row_or_404(conn, current_user["id"])
        secret = user_row["two_factor_secret"]
        if not secret or not bool(user_row["two_factor_pending"]):
            raise HTTPException(status_code=400, detail="2FA не запрошена")
        if not verify_totp(secret, data.code):
            raise HTTPException(status_code=400, detail="Неверный код 2FA")

        conn.execute(
            """
            UPDATE users
            SET is_2fa_enabled = 1, two_factor_pending = 0
            WHERE id = ?
            """,
            (user_row["id"],),
        )
        conn.commit()
        return {"ok": True}


@app.post("/api/v1/auth/2fa/disable")
async def disable_2fa(
    data: TwoFactorCodeRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, bool]:
    with get_connection() as conn:
        user_row = get_user_row_or_404(conn, current_user["id"])
        secret = user_row["two_factor_secret"]
        if not secret or not bool(user_row["is_2fa_enabled"]):
            raise HTTPException(status_code=400, detail="2FA не включена")
        if not verify_totp(secret, data.code):
            raise HTTPException(status_code=400, detail="Неверный код 2FA")

        conn.execute(
            """
            UPDATE users
            SET is_2fa_enabled = 0, two_factor_pending = 0
            WHERE id = ?
            """,
            (user_row["id"],),
        )
        conn.commit()
        return {"ok": True}


@app.post("/api/v1/auth/2fa/verify")
async def verify_login_2fa(data: TwoFactorVerifyRequest) -> dict[str, str]:
    with get_connection() as conn:
        challenge = conn.execute(
            "SELECT * FROM login_challenges WHERE id = ?",
            (data.otp_token,),
        ).fetchone()
        if not challenge:
            raise HTTPException(status_code=400, detail="Сессия 2FA не найдена или истекла")

        expires_at = from_iso(challenge["expires_at"])
        if not expires_at or expires_at <= utc_now():
            conn.execute("DELETE FROM login_challenges WHERE id = ?", (challenge["id"],))
            conn.commit()
            raise HTTPException(status_code=400, detail="Сессия 2FA истекла")

        user_row = get_user_by_id(conn, challenge["user_id"])
        if not user_row or not user_row["two_factor_secret"]:
            raise HTTPException(status_code=400, detail="Пользователь не найден")
        if not verify_totp(user_row["two_factor_secret"], data.code):
            raise HTTPException(status_code=400, detail="Неверный код 2FA")

        conn.execute("DELETE FROM login_challenges WHERE id = ?", (challenge["id"],))
        conn.commit()
        ensure_seeded_workspace(conn, user_row["id"])
        return create_auth_pair(conn, user_row)


@app.get("/api/v1/system/stats")
async def system_stats(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    with get_connection() as conn:
        user_id = current_user["id"]
        memory_entries = conn.execute(
            "SELECT COUNT(*) FROM memory_entries WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]
        devices_online = conn.execute(
            "SELECT COUNT(*) FROM devices WHERE user_id = ? AND is_online = 1",
            (user_id,),
        ).fetchone()[0]
        active_tasks = conn.execute(
            "SELECT COUNT(*) FROM agent_tasks WHERE user_id = ? AND status IN ('queued', 'running')",
            (user_id,),
        ).fetchone()[0]
        subscription_row = get_current_subscription_row(conn, user_id)
        subscription = build_subscription_payload(conn, subscription_row)
        return {
            "devices_online": devices_online,
            "memory_entries": memory_entries,
            "active_tasks": active_tasks,
            "quantum_status": "online",
            "subscription_tier": subscription["tariff"]["name"] if subscription and subscription.get("tariff") else "Free",
            "uptime_hours": max(int((time.time() - APP_STARTED_AT) // 3600), 0),
        }


@app.get("/api/v1/system/integrations")
async def system_integrations(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {
        "postgres": check_postgres_connection(),
        "redis": check_redis_connection(),
        "database_engine": "sqlite (core) + optional postgres/redis integrations",
    }


@app.get("/api/v1/memory/search")
async def search_memory(
    query: str = Query(default=""),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM memory_entries
            WHERE user_id = ?
            ORDER BY datetime(created_at) DESC
            """,
            (current_user["id"],),
        ).fetchall()
        scored: list[tuple[float, sqlite3.Row]] = []
        for row in rows:
            score = search_memory_score(row["content"], query)
            if query and score <= 0:
                continue
            scored.append((score, row))
        scored.sort(key=lambda item: (item[0], item[1]["id"]), reverse=True)
        return [serialize_memory(row, similarity=score if query else None) for score, row in scored[:limit]]


@app.post("/api/v1/memory/")
async def create_memory(
    payload: MemoryCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO memory_entries (user_id, content, importance, tags, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (current_user["id"], payload.content.strip(), payload.importance, json_dumps(payload.tags), iso_now()),
        )
        memory_row = conn.execute(
            "SELECT * FROM memory_entries WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (current_user["id"],),
        ).fetchone()
        conn.commit()
        return serialize_memory(memory_row)


@app.delete("/api/v1/memory/{memory_id}")
async def delete_memory(memory_id: int, current_user: dict[str, Any] = Depends(get_current_user)) -> Response:
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM memory_entries WHERE id = ? AND user_id = ?",
            (memory_id, current_user["id"]),
        )
        conn.commit()
    return Response(status_code=204)


@app.get("/api/v1/memory/count")
async def memory_count(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, int]:
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM memory_entries WHERE user_id = ?",
            (current_user["id"],),
        ).fetchone()[0]
        return {"count": count}


@app.get("/api/v1/smarthome/devices")
async def list_devices(current_user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM devices WHERE user_id = ? ORDER BY id ASC",
            (current_user["id"],),
        ).fetchall()
        return [serialize_device(row) for row in rows]


@app.post("/api/v1/smarthome/devices")
async def create_device(
    payload: DeviceCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO devices (user_id, name, device_type, room, protocol, is_online, state, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                current_user["id"],
                payload.name.strip(),
                payload.device_type,
                payload.room.strip() or "Без комнаты",
                payload.protocol,
                json_dumps({"power": False}),
                iso_now(),
            ),
        )
        row = conn.execute(
            "SELECT * FROM devices WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (current_user["id"],),
        ).fetchone()
        conn.commit()
        return serialize_device(row)


@app.delete("/api/v1/smarthome/devices/{device_id}")
async def delete_device(device_id: int, current_user: dict[str, Any] = Depends(get_current_user)) -> Response:
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM devices WHERE id = ? AND user_id = ?",
            (device_id, current_user["id"]),
        )
        conn.commit()
    return Response(status_code=204)


@app.post("/api/v1/smarthome/control")
async def control_device(
    payload: DeviceControlRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        if isinstance(payload.device_id, int):
            row = conn.execute(
                "SELECT * FROM devices WHERE id = ? AND user_id = ?",
                (payload.device_id, current_user["id"]),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM devices WHERE lower(name) = lower(?) AND user_id = ?",
                (str(payload.device_id), current_user["id"]),
            ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Устройство не найдено")

        state = json_loads(row["state"], {})
        command = payload.command
        if command == "turn_on":
            state["power"] = True
        elif command == "turn_off":
            state["power"] = False
        elif command == "lock":
            state["locked"] = True
        elif command == "unlock":
            state["locked"] = False
        elif command == "set_temperature":
            state["temperature"] = payload.params.get("value", payload.params.get("temperature", 22))
        elif "value" in payload.params:
            state[command] = payload.params["value"]
        else:
            state[command] = True

        conn.execute(
            "UPDATE devices SET state = ?, is_online = 1 WHERE id = ?",
            (json_dumps(state), row["id"]),
        )
        updated = conn.execute("SELECT * FROM devices WHERE id = ?", (row["id"],)).fetchone()
        conn.commit()
        return {"status": "ok", "device": serialize_device(updated)}


@app.post("/api/v1/smarthome/optimize")
async def optimize_home(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM devices WHERE user_id = ? ORDER BY id ASC",
            (current_user["id"],),
        ).fetchall()
        savings = round(max(len(rows) * 0.35, 0.8), 1)
        actions = [
            "Снизить яркость гостиной после 23:00",
            "Выключать офлайн-розетки ночью",
            "Поддерживать температуру 21-22°C в спальне",
        ]
        return {
            "savings_kwh": savings,
            "saved_kwh": savings,
            "actions": actions,
        }


@app.get("/api/v1/agents/")
async def list_agents(current_user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM agents WHERE user_id = ? ORDER BY id ASC",
            (current_user["id"],),
        ).fetchall()
        return [serialize_agent(row) for row in rows]


@app.post("/api/v1/agents/")
async def create_agent(
    payload: AgentCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO agents (user_id, name, agent_type, config, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (current_user["id"], payload.name.strip(), payload.agent_type, json_dumps(payload.config), iso_now()),
        )
        row = conn.execute(
            "SELECT * FROM agents WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (current_user["id"],),
        ).fetchone()
        conn.commit()
        return serialize_agent(row)


@app.delete("/api/v1/agents/{agent_id}")
async def delete_agent(agent_id: int, current_user: dict[str, Any] = Depends(get_current_user)) -> Response:
    with get_connection() as conn:
        conn.execute("DELETE FROM agents WHERE id = ? AND user_id = ?", (agent_id, current_user["id"]))
        conn.commit()
    return Response(status_code=204)


@app.get("/api/v1/agents/tasks")
async def list_tasks(current_user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM agent_tasks WHERE user_id = ? ORDER BY datetime(created_at) DESC, id DESC",
            (current_user["id"],),
        ).fetchall()
        return [serialize_task(row) for row in rows]


@app.post("/api/v1/agents/tasks")
async def create_task(
    payload: TaskCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        agent = conn.execute(
            "SELECT * FROM agents WHERE id = ? AND user_id = ?",
            (payload.agent_id, current_user["id"]),
        ).fetchone()
        if not agent:
            raise HTTPException(status_code=404, detail="Агент не найден")

        result = build_task_result(payload.action, payload.parameters)
        now = iso_now()
        conn.execute(
            """
            INSERT INTO agent_tasks (user_id, agent_id, action, parameters, status, result, error_message, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'completed', ?, NULL, ?, ?)
            """,
            (
                current_user["id"],
                payload.agent_id,
                payload.action,
                json_dumps(payload.parameters),
                json_dumps(result),
                now,
                now,
            ),
        )
        row = conn.execute(
            "SELECT * FROM agent_tasks WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (current_user["id"],),
        ).fetchone()
        conn.commit()
        return serialize_task(row)


@app.post("/api/v1/agents/tasks/{task_id}/cancel")
async def cancel_task(task_id: int, current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM agent_tasks WHERE id = ? AND user_id = ?",
            (task_id, current_user["id"]),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        conn.execute(
            """
            UPDATE agent_tasks
            SET status = 'cancelled', updated_at = ?
            WHERE id = ?
            """,
            (iso_now(), task_id),
        )
        updated = conn.execute("SELECT * FROM agent_tasks WHERE id = ?", (task_id,)).fetchone()
        conn.commit()
        return serialize_task(updated)


@app.post("/api/v1/agents/swarm")
async def run_swarm(
    payload: SwarmRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        agents = conn.execute(
            "SELECT * FROM agents WHERE user_id = ? ORDER BY id ASC",
            (current_user["id"],),
        ).fetchall()
        if not agents:
            raise HTTPException(status_code=400, detail="Сначала создайте хотя бы одного агента")

        created_ids: list[int] = []
        for agent in agents[:3]:
            now = iso_now()
            conn.execute(
                """
                INSERT INTO agent_tasks (user_id, agent_id, action, parameters, status, result, error_message, created_at, updated_at)
                VALUES (?, ?, 'swarm', ?, 'completed', ?, NULL, ?, ?)
                """,
                (
                    current_user["id"],
                    agent["id"],
                    json_dumps({"goal": payload.goal, "agent": agent["name"]}),
                    json_dumps(build_task_result("swarm", {"goal": payload.goal, "agent": agent["name"]})),
                    now,
                    now,
                ),
            )
            created_ids.append(conn.execute("SELECT last_insert_rowid()").fetchone()[0])
        conn.commit()
        return {
            "task_id": created_ids[0],
            "subtasks_created": len(created_ids),
            "goal": payload.goal,
        }


@app.get("/api/v1/payments/tariffs")
async def list_tariffs(current_user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tariffs WHERE is_active = 1 ORDER BY id ASC").fetchall()
        return [serialize_tariff(row) for row in rows]


@app.get("/api/v1/payments/subscriptions")
async def list_subscriptions(current_user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM subscriptions WHERE user_id = ? ORDER BY datetime(created_at) DESC",
            (current_user["id"],),
        ).fetchall()
        return [build_subscription_payload(conn, row) for row in rows]


@app.get("/api/v1/payments/subscriptions/current")
async def current_subscription(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    with get_connection() as conn:
        row = get_current_subscription_row(conn, current_user["id"])
        payload = build_subscription_payload(conn, row)
        if not payload:
            raise HTTPException(status_code=404, detail="Подписка не найдена")
        return payload


@app.post("/api/v1/payments/subscribe")
async def subscribe(
    request: Request,
    payload: SubscribeRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        tariff_row = get_tariff_by_id(conn, payload.tariff_id)
        if not tariff_row or not bool(tariff_row["is_active"]):
            raise HTTPException(status_code=404, detail="Тариф не найден")

        now = utc_now()
        current_row = get_current_subscription_row(conn, current_user["id"])
        if current_row and current_row["status"] == "active":
            conn.execute(
                """
                UPDATE subscriptions
                SET status = 'cancelled', auto_renew = 0, cancelled_at = ?
                WHERE id = ?
                """,
                (to_iso(now), current_row["id"]),
            )

        conn.execute(
            """
            INSERT INTO subscriptions (user_id, tariff_id, status, start_date, end_date, auto_renew, cancelled_at, created_at)
            VALUES (?, ?, 'active', ?, ?, ?, NULL, ?)
            """,
            (
                current_user["id"],
                tariff_row["id"],
                to_iso(now),
                to_iso(now + timedelta(days=tariff_row["duration_days"])),
                int(payload.save_payment_method),
                to_iso(now),
            ),
        )
        subscription_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        description = f"Подписка {tariff_row['name']} на {tariff_row['duration_days']} дней"
        payment_status = "succeeded"
        conn.execute(
            """
            INSERT INTO payments (user_id, subscription_id, amount, currency, status, description, created_at)
            VALUES (?, ?, ?, 'RUB', ?, ?, ?)
            """,
            (current_user["id"], subscription_id, tariff_row["price"], payment_status, description, iso_now()),
        )
        payment_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        confirmation_url = f"{str(request.base_url).rstrip('/')}/api/v1/payments/checkout/{payment_id}"
        return {
            "subscription_id": subscription_id,
            "payment_id": str(payment_id),
            "confirmation_url": confirmation_url,
            "tariff_name": tariff_row["name"],
            "amount": tariff_row["price"],
            "status": payment_status,
        }


@app.post("/api/v1/payments/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: int, current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM subscriptions WHERE id = ? AND user_id = ?",
            (subscription_id, current_user["id"]),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Подписка не найдена")
        conn.execute(
            """
            UPDATE subscriptions
            SET status = 'cancelled', auto_renew = 0, cancelled_at = ?
            WHERE id = ?
            """,
            (iso_now(), subscription_id),
        )
        updated = conn.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,)).fetchone()
        conn.commit()
        return build_subscription_payload(conn, updated)


@app.get("/api/v1/payments/payments")
async def list_payments(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM payments WHERE user_id = ? ORDER BY datetime(created_at) DESC, id DESC",
            (current_user["id"],),
        ).fetchall()
        return {
            "payments": [serialize_payment(row) for row in rows],
            "total": len(rows),
        }


@app.get("/api/v1/payments/checkout/{payment_id}", response_class=HTMLResponse)
async def payment_checkout_page(payment_id: int) -> HTMLResponse:
    with get_connection() as conn:
        payment_row = conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
        if not payment_row:
            raise HTTPException(status_code=404, detail="Платёж не найден")
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8" />
        <title>Aurion Payment</title>
        <style>
          body {{
            margin: 0;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            background: radial-gradient(circle at top, #16323f, #061116 68%);
            color: #e8fbff;
            min-height: 100vh;
            display: grid;
            place-items: center;
          }}
          .card {{
            width: min(92vw, 520px);
            border: 1px solid rgba(116, 224, 255, 0.25);
            border-radius: 20px;
            background: rgba(4, 14, 19, 0.86);
            padding: 28px;
            box-shadow: 0 18px 60px rgba(0, 0, 0, 0.35);
          }}
          .ok {{
            font-size: 44px;
            margin-bottom: 12px;
          }}
          h1 {{
            margin: 0 0 12px;
            font-size: 20px;
            letter-spacing: 0.08em;
          }}
          p {{
            color: #9cc7d4;
            line-height: 1.5;
          }}
        </style>
      </head>
      <body>
        <div class="card">
          <div class="ok">OK</div>
          <h1>Платёж #{payment_id} подтверждён</h1>
          <p>Подписка уже активирована в MVP-режиме. Эту вкладку можно закрыть и вернуться в Aurion.</p>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/api/v1/finance/accounts")
async def list_accounts(current_user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM finance_accounts WHERE user_id = ? ORDER BY id ASC",
            (current_user["id"],),
        ).fetchall()
        return [serialize_account(row) for row in rows]


@app.get("/api/v1/finance/accounts/{account_id}/transactions")
async def list_transactions(
    account_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM transactions
            WHERE user_id = ? AND account_id = ?
            ORDER BY datetime(date) DESC, id DESC
            LIMIT ?
            """,
            (current_user["id"], account_id, limit),
        ).fetchall()
        return [serialize_transaction(row) for row in rows]


@app.get("/api/v1/finance/analytics")
async def finance_analytics(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY datetime(date) DESC",
            (current_user["id"],),
        ).fetchall()
        total_income = sum(float(row["amount"]) for row in rows if row["type"] == "credit")
        total_expenses = sum(abs(float(row["amount"])) for row in rows if row["type"] == "debit")
        by_category: dict[str, float] = {}
        for row in rows:
            if row["type"] != "debit":
                continue
            by_category[row["category"]] = by_category.get(row["category"], 0.0) + abs(float(row["amount"]))
        return {
            "total_income": f"{total_income:.2f}",
            "total_expenses": f"{total_expenses:.2f}",
            "by_category": {key: f"{value:.2f}" for key, value in by_category.items()},
            "period": "30d",
        }


@app.get("/api/v1/finance/tips")
async def finance_tips(current_user: dict[str, Any] = Depends(get_current_user)) -> list[str]:
    return [
        "Проверьте повторяющиеся подписки и отключите неиспользуемые.",
        "Для бытовых покупок полезно установить еженедельный лимит.",
        "Сравните траты на транспорт с абонементами и фиксированными маршрутами.",
    ]


@app.get("/api/v1/profile/preferences")
async def profile_preferences(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    with get_connection() as conn:
        return get_user_preferences(conn, current_user["id"])


@app.put("/api/v1/profile/preferences/voice")
async def update_voice_preferences(
    payload: VoicePreferencesUpdateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        return update_user_preferences(conn, current_user["id"], payload.persona)


@app.post("/api/v1/voice/profiles/enroll")
async def enroll_voice_profile(
    payload: VoiceProfileEnrollRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    fingerprint = voice_fingerprint(payload.audio_sample_b64)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO voice_profiles (user_id, profile_name, fingerprint, provider, created_at)
            VALUES (?, ?, ?, 'mvp-hash', ?)
            """,
            (current_user["id"], payload.profile_name.strip(), fingerprint, iso_now()),
        )
        voice_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        return {"id": voice_id, "profile_name": payload.profile_name.strip(), "provider": "mvp-hash"}


@app.post("/api/v1/voice/profiles/identify")
async def identify_voice_profile(
    payload: VoiceIdentifyRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    target = voice_fingerprint(payload.audio_sample_b64)
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM voice_profiles WHERE user_id = ? ORDER BY id ASC",
            (current_user["id"],),
        ).fetchall()
        if not rows:
            return {"matched": False, "reason": "Нет сохранённых голосовых профилей"}
        best = None
        for row in rows:
            score = sum(1 for a, b in zip(target, row["fingerprint"]) if a == b) / max(len(target), 1)
            if best is None or score > best["score"]:
                best = {"score": score, "profile_name": row["profile_name"], "id": row["id"]}
        return {
            "matched": bool(best and best["score"] > 0.7),
            "confidence": round(best["score"], 3) if best else 0.0,
            "profile_name": best["profile_name"] if best else None,
            "profile_id": best["id"] if best else None,
            "provider": "mvp-hash",
        }


@app.post("/api/v1/proactive/generate")
async def generate_proactive(
    payload: ProactiveGenerateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        prefs = get_user_preferences(conn, current_user["id"])
        if not prefs.get("proactive_enabled", True):
            return {"generated": 0, "suggestions": []}
        suggestions = generate_proactive_suggestions(conn, current_user["id"], payload.lookback_days)
        return {"generated": len(suggestions), "suggestions": suggestions}


@app.get("/api/v1/proactive/suggestions")
async def list_proactive_suggestions(current_user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM proactive_suggestions
            WHERE user_id = ?
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT 20
            """,
            (current_user["id"],),
        ).fetchall()
        return [
            {
                "id": row["id"],
                "message": row["message"],
                "confidence": round(float(row["confidence"]), 2),
                "source": row["source"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]


@app.get("/api/v1/diy/instructions")
async def diy_instructions(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    mqtt_host = config_get("MQTT_HOST", "mqtt://broker.hivemq.com")
    return {
        "quickstart": [
            "Подключите ESP8266/Arduino к Wi-Fi.",
            "Настройте MQTT клиент и топик aurion/{user_id}/devices/{device}.",
            "Отправляйте JSON-стейт устройства каждые 15-60 секунд.",
        ],
        "mqtt_host": mqtt_host,
        "example_topics": [
            f"aurion/{current_user['id']}/devices/kitchen-light/state",
            f"aurion/{current_user['id']}/devices/door-sensor/events",
        ],
        "sample_payload": {"power": True, "temperature": 22, "humidity": 45},
    }


@app.post("/api/v1/diy/sketches")
async def upload_diy_sketch(
    payload: DIYSketchUploadRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO diy_sketches (user_id, name, device_type, board, protocol, sketch_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user["id"],
                payload.name.strip(),
                payload.device_type.strip(),
                payload.board.strip(),
                payload.protocol.strip(),
                payload.sketch_code,
                iso_now(),
            ),
        )
        sketch_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        return {"id": sketch_id, "status": "stored"}


@app.get("/api/v1/diy/sketches")
async def list_diy_sketches(current_user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM diy_sketches WHERE user_id = ? ORDER BY id DESC LIMIT 50",
            (current_user["id"],),
        ).fetchall()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "device_type": row["device_type"],
                "board": row["board"],
                "protocol": row["protocol"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]


@app.post("/api/v1/quantum/route")
async def quantum_route(
    payload: QuantumRouteRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    from app.quantum_router import QuantumRouter

    router = QuantumRouter(
        quantum_token=config_get("QUANTUM_RINGS_TOKEN"),
        hpc_url=config_get("HPC_UNICORE_URL"),
        hpc_user=config_get("HPC_UNICORE_USER"),
        hpc_password=config_get("HPC_UNICORE_PASSWORD"),
    )
    return router.route_task(
        task_type=payload.task_type,
        payload=payload.payload,
        preferred_backend=payload.preferred_backend,
    )


@app.post("/api/v1/guardian/scan")
async def guardian_scan(
    payload: GuardianScanRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    hosts = payload.hosts[:16]
    report: list[dict[str, Any]] = []
    for host in hosts:
        open_ports = scan_host_ports(host, payload.ports, payload.timeout_seconds)
        risks = []
        if 23 in open_ports:
            risks.append("Открыт Telnet — высокий риск, выключите доступ.")
        if 1883 in open_ports:
            risks.append("MQTT без TLS: рекомендуется 8883 + авторизация.")
        if 5432 in open_ports or 3306 in open_ports:
            risks.append("Порт БД открыт в LAN/наружу, ограничьте firewall по IP.")
        report.append(
            {
                "host": host,
                "open_ports": open_ports,
                "risks": risks,
                "score": max(0, 100 - len(risks) * 20 - len(open_ports) * 2),
            }
        )
    return {
        "scanned_hosts": len(report),
        "report": report,
        "recommendations": [
            "Выключить UPnP на роутере, если не используете.",
            "Включить WPA2/WPA3 и сложный пароль Wi-Fi.",
            "Ограничить доступ к панели роутера только из локальной сети.",
        ],
    }


@app.get("/api/v1/guardian/router-audit")
async def guardian_router_audit(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {
        "checks": [
            {"item": "WPS", "status": "warning", "message": "Рекомендуется отключить WPS."},
            {"item": "UPnP", "status": "warning", "message": "Отключите UPnP, если нет строгой необходимости."},
            {"item": "Admin password", "status": "ok", "message": "Похоже, пароль изменён с заводского."},
            {"item": "Remote admin", "status": "warning", "message": "Ограничьте удалённый админ-доступ по IP."},
        ]
    }


@app.get("/api/v1/config")
async def config_snapshot(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if current_user["role"] not in {"creator", "admin"}:
        raise HTTPException(status_code=403, detail="Только создатель или администратор")
    visible = {}
    for key in sorted(RUNTIME_CONFIG_KEYS):
        value = config_get(key)
        if value:
            visible[key] = mask_secret(value)
    return {"keys": visible, "updated_at": iso_now()}


@app.post("/api/v1/config/update")
async def update_config(
    payload: ConfigUpdateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user["role"] not in {"creator", "admin"}:
        raise HTTPException(status_code=403, detail="Только создатель или администратор")
    if not payload.updates:
        return {"updated": 0, "keys": []}

    updated_keys: list[str] = []
    for key, value in payload.updates.items():
        if key not in RUNTIME_CONFIG_KEYS:
            continue
        normalized = str(value).strip()
        if normalized:
            RUNTIME_CONFIG[key] = normalized
            updated_keys.append(key)
        elif key in RUNTIME_CONFIG:
            del RUNTIME_CONFIG[key]
            updated_keys.append(key)
    save_runtime_config(RUNTIME_CONFIG)
    return {"updated": len(updated_keys), "keys": sorted(updated_keys)}


@app.websocket("/api/v1/voice/ws")
async def voice_ws(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    payload = decode_access_token(token or "")
    if not payload:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    with get_connection() as conn:
        user_row = get_user_by_id(conn, payload["sub"])
        if not user_row:
            await websocket.close(code=4404)
            return
        prefs = get_user_preferences(conn, user_row["id"])
        await websocket.send_json(
            {
                "type": "chat_response",
                "content": f"Привет, {user_row['username']}. Я онлайн и готов помочь.",
                "voice_persona": prefs["voice_persona"],
            }
        )

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                message = {"content": raw}

            content = str(message.get("content") or message.get("text") or "").strip()
            if not content:
                await websocket.send_json({"type": "error", "content": "Пустое сообщение"})
                continue

            with get_connection() as conn:
                prefs = get_user_preferences(conn, payload["sub"])
                reply = build_chat_reply(conn, payload["sub"], content)
            emotion = infer_emotion(content, prefs["voice_persona"])
            tts = synthesize_tts(reply, emotion, prefs["voice_persona"])
            await websocket.send_json(
                {
                    "type": "chat_response",
                    "content": reply,
                    "emotion": emotion,
                    "voice_persona": prefs["voice_persona"],
                    "tts": tts,
                }
            )
    except WebSocketDisconnect:
        return
