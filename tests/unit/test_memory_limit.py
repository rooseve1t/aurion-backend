"""
Тест лимита памяти: при добавлении 10 001-й записи удаляется наименее важная.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_memory_limit_removes_least_important():
    """При добавлении 10 001-й записи должна удаляться запись с наименьшим importance."""
    from app.services.memory_service import MemoryService

    # Мокаем сессию БД
    mock_db = AsyncMock(spec=AsyncSession)

    # Мокаем count — возвращает 10 000 (лимит достигнут)
    count_result = MagicMock()
    count_result.scalar.return_value = 10_000

    # Мокаем жертву — запись с importance=1
    victim = MagicMock()
    victim_result = MagicMock()
    victim_result.scalar_one_or_none.return_value = victim

    # execute возвращает разные результаты для count и для поиска жертвы
    mock_db.execute = AsyncMock(side_effect=[count_result, victim_result])
    mock_db.delete = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    service = MemoryService(mock_db)

    with patch.object(service, "_mock_quantum_encrypt", return_value="encrypted"):
        with patch("app.services.memory_service._encode_text", return_value=[0.0] * 384):
            await service.add_memory(
                user_id="user-1",
                content="Новое воспоминание",
                importance=8,
            )

    # Проверяем что delete был вызван (жертва удалена)
    mock_db.delete.assert_called_once_with(victim)
    mock_db.flush.assert_called_once()
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_memory_no_deletion_when_under_limit():
    """Если записей меньше 10 000 — удаления не происходит."""
    from app.services.memory_service import MemoryService

    mock_db = AsyncMock(spec=AsyncSession)

    count_result = MagicMock()
    count_result.scalar.return_value = 500  # далеко от лимита

    mock_db.execute = AsyncMock(return_value=count_result)
    mock_db.delete = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    service = MemoryService(mock_db)

    with patch.object(service, "_mock_quantum_encrypt", return_value="encrypted"):
        with patch("app.services.memory_service._encode_text", return_value=[0.0] * 384):
            await service.add_memory(
                user_id="user-1",
                content="Воспоминание в пределах лимита",
                importance=5,
            )

    # Удаления не должно быть
    mock_db.delete.assert_not_called()
    mock_db.add.assert_called_once()
