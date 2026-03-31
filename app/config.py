import logging
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator

logger = logging.getLogger("aurion-config")


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"

    # CORS
    ALLOWED_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,"
        "https://aurionai.ru,https://www.aurionai.ru"
    )

    # Database — SQLite для dev, PostgreSQL для prod
    DATABASE_URL: str = "sqlite+aiosqlite:///./aurion.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Encryption
    ENCRYPTION_KEY: str = ""  # 32-байтный hex для AES-256-GCM

    # Quantum
    QUANTUM_RINGS_TOKEN: str = "s_977d151d919a41738625077677c3723f"
    IBM_QUANTUM_TOKEN: str = ""
    PASQAL_TOKEN: str = ""
    DWAVE_API_TOKEN: str = ""

    # AI / LLM
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Yandex
    YANDEX_API_KEY: str = ""
    YANDEX_FOLDER_ID: str = ""
    YANDEX_IAM_TOKEN: str = ""

    # Voice / TTS
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "pNInz6obpgDQGcFmaJgB"  # Adam — deep male voice
    ELEVENLABS_STABILITY: float = 0.75
    ELEVENLABS_SIMILARITY_BOOST: float = 0.85
    ELEVENLABS_STYLE: float = 0.2

    # OSINT
    CENSYS_API_ID: str = ""
    CENSYS_API_SECRET: str = ""
    SHODAN_API_KEY: str = ""
    APIFY_API_TOKEN: str = ""

    # Satellite
    PLANET_API_KEY: str = ""

    # Payments
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""

    # Health / Wearables
    GOOGLE_FIT_CLIENT_ID: str = ""
    GOOGLE_FIT_CLIENT_SECRET: str = ""
    FITBIT_CLIENT_ID: str = ""
    FITBIT_CLIENT_SECRET: str = ""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # Creative
    REPLICATE_API_TOKEN: str = ""
    HUGGINGFACE_TOKEN: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    # Voice STT
    VOSK_MODEL_PATH: str = "models/vosk-model-small-ru-0.22"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def warn_sqlite_in_production(cls, v: str, info: object) -> str:
        import os
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production" and "sqlite" in v.lower():
            logger.warning(
                "⚠️  SQLite detected in PRODUCTION environment! "
                "Set DATABASE_URL to a PostgreSQL connection string."
            )
        return v


settings = Settings()
