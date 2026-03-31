"""
Smoke-тесты для Feed API роутера.
"""
import pytest
from app.api.feed import _card_to_dict, PAGE_SIZE


def test_page_size():
    assert PAGE_SIZE == 20


def test_card_to_dict_basic():
    """_card_to_dict корректно сериализует FeedCard."""
    import uuid
    from datetime import datetime, timezone
    from unittest.mock import MagicMock

    card = MagicMock()
    card.id = uuid.uuid4()
    card.type = "alert"
    card.domain = "finance"
    card.title = "Test title"
    card.body = "Test body"
    card.priority = "high"
    card.requires_confirmation = False
    card.confirmed_at = None
    card.dismissed_at = None
    card.created_at = datetime.now(timezone.utc)
    card.user_id = uuid.uuid4()

    result = _card_to_dict(card)

    assert result["type"] == "alert"
    assert result["domain"] == "finance"
    assert result["title"] == "Test title"
    assert result["requiresConfirmation"] is False
    assert result["confirmedAt"] is None
    assert result["dismissedAt"] is None
    assert "id" in result
    assert "userId" in result
    assert "createdAt" in result


def test_card_to_dict_with_timestamps():
    """_card_to_dict корректно форматирует временные метки."""
    import uuid
    from datetime import datetime, timezone
    from unittest.mock import MagicMock

    now = datetime.now(timezone.utc)
    card = MagicMock()
    card.id = uuid.uuid4()
    card.type = "suggestion"
    card.domain = "calendar"
    card.title = "Meeting"
    card.body = "Confirm meeting"
    card.priority = "medium"
    card.requires_confirmation = True
    card.confirmed_at = now
    card.dismissed_at = None
    card.created_at = now
    card.user_id = uuid.uuid4()

    result = _card_to_dict(card)

    assert result["requiresConfirmation"] is True
    assert result["confirmedAt"] is not None
    assert result["dismissedAt"] is None


def test_feed_router_exists():
    """Feed роутер импортируется без ошибок."""
    from app.api.feed import router
    assert router is not None
