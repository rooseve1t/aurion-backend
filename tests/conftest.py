"""
Test configuration and setup for Aurion Backend tests
"""

import os
import sys
import pytest
import asyncio
from collections.abc import AsyncIterator
import pytest_asyncio

# Set required environment variables for testing
os.environ.setdefault('ENCRYPTION_KEY', 'test-encryption-key-for-testing-only=')
os.environ.setdefault('AURION_SECRET_KEY', 'test-secret-key-for-testing')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '30')
os.environ.setdefault('REFRESH_TOKEN_EXPIRE_DAYS', '30')
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///./test_aurion.db')
os.environ.setdefault('APP_BASE_URL', 'http://localhost:8000')

# Now import the app
sys.path.insert(0, '/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend')

# Generate proper Fernet key if needed
from cryptography.fernet import Fernet
try:
    test_key = Fernet.generate_key().decode()
    os.environ['ENCRYPTION_KEY'] = test_key
except Exception:
    pass  # Use default if generation fails


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """Initialize test database before running tests"""
    from app.database_final import init_db, close_db

    asyncio.run(init_db())
    
    yield
    
    # Cleanup after tests
    try:
        asyncio.run(close_db())
    except Exception:
        pass


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[object]:
    """Async DB session fixture for tests that need direct service access."""
    from app.database_final import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        yield session
