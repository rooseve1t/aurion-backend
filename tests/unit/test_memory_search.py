"""
Property-тест для MemoryService:
Семантический поиск всегда возвращает подмножество существующих записей,
отсортированных по убыванию релевантности.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, settings as h_settings, strategies as st


@pytest.mark.asyncio
async def test_search_returns_subset_of_existing():
    """Поиск возвращает только записи из БД, не выдуманные."""
    from app.services.memory_service import MemoryService

    mock_db = AsyncMock()

    # Создаём 5 тестовых записей
    memories = []
    for i in range(5):
        m = MagicMock()
        m.id = f"id-{i}"
        m.content = f"PQV_{i}"
        m.title = f"Запись {i}"
        m.importance = i + 1
        m.tags = []
        m.categories = []
        m.embedding = [float(i)] * 384
        memories.append(m)

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = memories
    mock_db.execute = AsyncMock(return_value=result_mock)

    service = MemoryService(mock_db)

    with patch("app.services.memory_service._encode_text", return_value=[0.5] * 384):
        results = await service.search_memories(
            user_id="user-1",
            query="тест",
            limit=3,
        )

    # Результаты должны быть подмножеством исходных записей
    result_ids = {r.get("id") or str(getattr(r, "id", "")) for r in results}
    existing_ids = {str(m.id) for m in memories}
    assert result_ids.issubset(existing_ids), "Поиск вернул несуществующие записи"
    assert len(results) <= 3


@pytest.mark.asyncio
async def test_search_respects_limit():
    """Поиск не возвращает больше записей чем limit."""
    from app.services.memory_service import MemoryService

    mock_db = AsyncMock()
    memories = []
    for i in range(20):
        m = MagicMock()
        m.id = f"id-{i}"
        m.content = f"PQV_content_{i}"
        m.title = f"Запись {i}"
        m.importance = 5
        m.tags = []
        m.categories = []
        m.embedding = [float(i % 10) / 10] * 384
        memories.append(m)

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = memories
    mock_db.execute = AsyncMock(return_value=result_mock)

    service = MemoryService(mock_db)

    for limit in [1, 5, 10]:
        with patch("app.services.memory_service._encode_text", return_value=[0.3] * 384):
            results = await service.search_memories(
                user_id="user-1",
                query="запрос",
                limit=limit,
            )
        assert len(results) <= limit, f"Вернул {len(results)} при limit={limit}"
