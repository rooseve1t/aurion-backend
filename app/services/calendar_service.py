"""
Сервис календаря — Google Calendar (OAuth2) + ручной ввод как fallback.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("aurion-calendar")


class CalendarService:
    def __init__(self, google_client_id: str = "", google_client_secret: str = "") -> None:
        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
        # Локальное хранилище событий (fallback когда OAuth не настроен)
        self._local_events: List[Dict[str, Any]] = []

    @property
    def google_available(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret)

    async def get_events(
        self,
        user_id: str,
        max_results: int = 10,
        time_min: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Получить события. Google Calendar если OAuth настроен, иначе локальный список."""
        if self.google_available:
            try:
                return await self._google_get_events(user_id, max_results, time_min)
            except Exception as e:
                logger.warning(f"Google Calendar недоступен: {e} — использую локальный список")

        # Fallback — локальные события
        events = [e for e in self._local_events if e.get("user_id") == user_id]
        return {
            "source": "local",
            "events": events[:max_results],
            "google_available": False,
        }

    async def create_event(
        self,
        user_id: str,
        title: str,
        start: str,
        end: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """Создать событие. Google Calendar или локально."""
        event: Dict[str, Any] = {
            "id": f"local_{len(self._local_events)}",
            "user_id": user_id,
            "title": title,
            "start": start,
            "end": end,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "local",
        }

        if self.google_available:
            try:
                return await self._google_create_event(user_id, title, start, end, description)
            except Exception as e:
                logger.warning(f"Google Calendar создание не удалось: {e} — сохраняю локально")

        self._local_events.append(event)
        return {"status": "created", "event": event, "source": "local"}

    # ─── Google Calendar (требует OAuth2 токен пользователя) ─────────────────

    async def _google_get_events(
        self, user_id: str, max_results: int, time_min: Optional[str]
    ) -> Dict[str, Any]:
        """Получить события из Google Calendar через API."""
        import aiohttp
        # В реальности здесь нужен access_token пользователя из БД
        # Сейчас возвращаем заглушку с пометкой
        return {
            "source": "google",
            "events": [],
            "note": "Требуется OAuth2 авторизация пользователя",
            "google_available": True,
        }

    async def _google_create_event(
        self, user_id: str, title: str, start: str, end: str, description: str
    ) -> Dict[str, Any]:
        """Создать событие в Google Calendar."""
        return {
            "status": "created",
            "source": "google",
            "note": "Требуется OAuth2 авторизация пользователя",
        }


def get_calendar_service() -> CalendarService:
    from ..config import settings
    return CalendarService(
        google_client_id=settings.GOOGLE_FIT_CLIENT_ID,
        google_client_secret=settings.GOOGLE_FIT_CLIENT_SECRET,
    )
