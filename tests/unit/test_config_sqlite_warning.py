"""
Тест 1.7: при старте с ENVIRONMENT=production и DATABASE_URL=sqlite://...
логируется WARNING через aurion-config logger.
"""
import logging
import pytest
from unittest.mock import patch


def _make_settings(environment: str, database_url: str):
    """Создаёт экземпляр Settings с заданными env-переменными."""
    from app.config import Settings

    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": environment, "DATABASE_URL": database_url},
        clear=False,
    ):
        return Settings(
            ENVIRONMENT=environment,
            DATABASE_URL=database_url,
            _env_file=None,  # не читать .env файл
        )


def test_sqlite_in_production_logs_warning(caplog):
    """SQLite + production -> WARNING в логе aurion-config."""
    with caplog.at_level(logging.WARNING, logger="aurion-config"):
        _make_settings(
            environment="production",
            database_url="sqlite+aiosqlite:///./aurion.db",
        )

    assert any(
        "SQLite" in record.message and record.levelno == logging.WARNING
        for record in caplog.records
    ), "Ожидался WARNING о SQLite в production, но он не был залогирован"


def test_sqlite_in_development_no_warning(caplog):
    """SQLite + development -> WARNING не логируется."""
    with caplog.at_level(logging.WARNING, logger="aurion-config"):
        _make_settings(
            environment="development",
            database_url="sqlite+aiosqlite:///./aurion.db",
        )

    sqlite_warnings = [
        r for r in caplog.records
        if "SQLite" in r.message and r.levelno == logging.WARNING
    ]
    assert not sqlite_warnings, "WARNING о SQLite не должен логироваться в development"


def test_postgres_in_production_no_warning(caplog):
    """PostgreSQL + production -> WARNING не логируется."""
    with caplog.at_level(logging.WARNING, logger="aurion-config"):
        _make_settings(
            environment="production",
            database_url="postgresql+asyncpg://user:pass@localhost/aurion",
        )

    sqlite_warnings = [
        r for r in caplog.records
        if "SQLite" in r.message and r.levelno == logging.WARNING
    ]
    assert not sqlite_warnings, "WARNING о SQLite не должен логироваться при PostgreSQL"
