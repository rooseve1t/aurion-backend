from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))

from app.database import Base
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import declarative_base

# Импортируем модели для autogenerate
try:
    from app.models import *  # noqa: F401,F403
    from app.database import metadata
    target_metadata = metadata
except ImportError:
    # Если еще нет базы данных, создаем базовую метадату
    from sqlalchemy import MetaData
    target_metadata = MetaData()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url() -> str:
    """Получаем URL базы данных из переменных окружения или конфига"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fallback для разработки
        postgres_user = os.getenv("POSTGRES_USER", "aurion")
        postgres_password = os.getenv("POSTGRES_PASSWORD", "password")
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        postgres_db = os.getenv("POSTGRES_DB", "aurion")
        database_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    return database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = create_async_engine(
        configuration["sqlalchemy.url"],
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
