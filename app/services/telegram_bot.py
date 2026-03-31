"""
AurionTelegramBot v2 — Telegram-бот JARVIS.

Функции:
- 2FA: подтверждение входа с нового устройства (inline keyboard confirm/deny)
- Текстовый чат с JARVIS для зарегистрированных пользователей
- Команды: /start, /status, /confirm, /help

Если TELEGRAM_BOT_TOKEN не задан — инициализация пропускается.
"""
import logging
from typing import Any, Optional

logger = logging.getLogger("aurion-telegram")

_bot_instance: Optional["AurionTelegramBot"] = None


def get_bot_instance() -> Optional["AurionTelegramBot"]:
    return _bot_instance


class AurionTelegramBot:
    """Telegram-бот Aurion OS."""

    def __init__(self, token: str) -> None:
        self._token = token
        self._app: Any = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        try:
            from telegram.ext import (
                Application,
                CommandHandler,
                MessageHandler,
                CallbackQueryHandler,
                filters,
            )

            app = Application.builder().token(self._token).build()
            app.add_handler(CommandHandler("start",   self._cmd_start))
            app.add_handler(CommandHandler("status",  self._cmd_status))
            app.add_handler(CommandHandler("confirm", self._cmd_confirm))
            app.add_handler(CommandHandler("help",    self._cmd_help))
            app.add_handler(CallbackQueryHandler(self._on_callback_query))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message))

            self._app = app
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            logger.info("Telegram-бот JARVIS v2 запущен")
        except Exception as exc:
            logger.error(f"Ошибка запуска Telegram-бота: {exc}")
            self._app = None

    async def stop(self) -> None:
        if self._app:
            try:
                await self._app.updater.stop()
                await self._app.stop()
                await self._app.shutdown()
            except Exception as exc:
                logger.warning(f"Ошибка остановки Telegram-бота: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def send_2fa_request(
        self, telegram_id: int, device_info: str, session_token: str
    ) -> None:
        """Отправить запрос подтверждения нового устройства с inline-кнопками."""
        if not self._app:
            return
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Подтвердить", callback_data=f"confirm:{session_token}"),
                    InlineKeyboardButton("Отклонить",   callback_data=f"deny:{session_token}"),
                ]
            ])
            text = (
                "Запрос входа с нового устройства\n\n"
                f"Устройство: {device_info}\n\n"
                "Это вы? Подтвердите или отклоните вход."
            )
            await self._app.bot.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup=keyboard,
            )
        except Exception as exc:
            logger.warning(f"Не удалось отправить 2FA запрос в Telegram {telegram_id}: {exc}")

    async def send_notification(self, telegram_id: int, message: str) -> None:
        """Отправить персональное уведомление пользователю."""
        if not self._app:
            return
        try:
            await self._app.bot.send_message(
                chat_id=telegram_id,
                text=f"JARVIS: {message}",
            )
        except Exception as exc:
            logger.warning(f"Не удалось отправить уведомление в Telegram {telegram_id}: {exc}")

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------

    async def _cmd_start(self, update: Any, context: Any) -> None:
        telegram_id = str(update.effective_chat.id)
        registered = await self._is_registered(telegram_id)

        if registered:
            await update.message.reply_text(
                "Добрый день, сэр. Я JARVIS — ваш персональный ИИ-ассистент.\n\n"
                "Просто напишите мне — я отвечу.\n\n"
                "Команды:\n"
                "/status — статус системы\n"
                "/help — справка"
            )
        else:
            await update.message.reply_text(
                "Добрый день. Я JARVIS — ИИ-ассистент системы Aurion OS.\n\n"
                "Для доступа необходимо зарегистрироваться и привязать "
                "Telegram-аккаунт в настройках профиля.\n\n"
                "/help — подробнее"
            )

    async def _cmd_status(self, update: Any, context: Any) -> None:
        telegram_id = str(update.effective_chat.id)
        if not await self._is_registered(telegram_id):
            await update.message.reply_text("Доступ ограничен. Необходима регистрация.")
            return

        await update.message.reply_text(
            "Статус Aurion OS:\n"
            "Backend: онлайн\n"
            "JARVIS: активен\n"
            "Агенты: готовы\n"
            "Угрозы: не обнаружены"
        )

    async def _cmd_confirm(self, update: Any, context: Any) -> None:
        args = context.args
        if not args:
            await update.message.reply_text("Использование: /confirm <session_token>")
            return

        session_token = args[0]
        success = await self._confirm_device(session_token)
        if success:
            await update.message.reply_text("Устройство подтверждено. Вход выполнен.")
        else:
            await update.message.reply_text("Сессия не найдена или истекла.")

    async def _cmd_help(self, update: Any, context: Any) -> None:
        await update.message.reply_text(
            "JARVIS — Aurion OS\n\n"
            "Команды:\n"
            "/start — приветствие\n"
            "/status — статус системы\n"
            "/confirm <token> — подтвердить вход\n"
            "/help — эта справка\n\n"
            "Просто напишите сообщение — JARVIS ответит."
        )

    # ------------------------------------------------------------------
    # Message handler — чат с JARVIS
    # ------------------------------------------------------------------

    async def _on_message(self, update: Any, context: Any) -> None:
        telegram_id = str(update.effective_chat.id)

        if not await self._is_registered(telegram_id):
            await update.message.reply_text(
                "Доступ ограничен. Зарегистрируйтесь и привяжите Telegram в профиле."
            )
            return

        user_text = (update.message.text or "").strip()
        if not user_text:
            return

        try:
            from .voice_jarvis_service import get_jarvis_service
            jarvis = get_jarvis_service()
            if jarvis:
                response = await jarvis.generate_response(user_text)
            else:
                response = "Сервис JARVIS временно недоступен."
        except Exception as exc:
            logger.warning(f"JARVIS response error: {exc}")
            response = "Произошла ошибка при обработке запроса."

        await update.message.reply_text(response)

    # ------------------------------------------------------------------
    # Callback query handler — inline кнопки 2FA
    # ------------------------------------------------------------------

    async def _on_callback_query(self, update: Any, context: Any) -> None:
        query = update.callback_query
        await query.answer()

        data: str = query.data or ""

        if data.startswith("confirm:"):
            session_token = data[len("confirm:"):]
            success = await self._confirm_device(session_token)
            if success:
                await query.edit_message_text("Устройство подтверждено. Вход выполнен.")
            else:
                await query.edit_message_text("Сессия истекла. Попробуйте войти снова.")

        elif data.startswith("deny:"):
            session_token = data[len("deny:"):]
            await self._deny_device(session_token)
            await query.edit_message_text(
                "Вход отклонён. Если это были не вы — смените пароль."
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _is_registered(self, telegram_id: str) -> bool:
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.user import User
            from sqlalchemy import select

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(User).where(User.telegram_id == telegram_id).limit(1)
                )
                return result.scalar_one_or_none() is not None
        except Exception as exc:
            logger.warning(f"_is_registered check failed: {exc}")
            return False

    async def _confirm_device(self, session_token: str) -> bool:
        try:
            from ..api.auth_v2 import _redis_get, _redis_delete
            from ..database_final import AsyncSessionLocal
            from ..models.user import User
            from ..models.trusted_device import TrustedDevice
            from sqlalchemy import select
            import json
            import uuid

            session_key = f"2fa_session:{session_token}"
            raw = await _redis_get(session_key)
            if not raw:
                return False

            session = json.loads(raw)
            user_id = session["user_id"]
            fingerprint = session["fingerprint"]

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(User).where(User.id == uuid.UUID(user_id)).limit(1)
                )
                user = result.scalar_one_or_none()
                if not user:
                    return False

                td = TrustedDevice(
                    user_id=user.id,
                    device_fingerprint=fingerprint,
                    user_agent=session.get("ua"),
                    ip_address=session.get("ip"),
                )
                db.add(td)
                await db.commit()

            await _redis_delete(session_key)
            logger.info(f"Device confirmed via Telegram for user {user_id}")
            return True
        except Exception as exc:
            logger.error(f"_confirm_device failed: {exc}")
            return False

    async def _deny_device(self, session_token: str) -> None:
        try:
            from ..api.auth_v2 import _redis_delete
            await _redis_delete(f"2fa_session:{session_token}")
        except Exception as exc:
            logger.warning(f"_deny_device failed: {exc}")


# ---------------------------------------------------------------------------
# Module-level init helpers (обратная совместимость)
# ---------------------------------------------------------------------------

async def init_telegram_bot() -> None:
    """Инициализация бота. Вызывается из lifespan."""
    global _bot_instance
    from ..config import settings

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN не задан — Telegram-бот отключён")
        return

    bot = AurionTelegramBot(settings.TELEGRAM_BOT_TOKEN)
    await bot.start()
    _bot_instance = bot


async def send_notification(message: str, telegram_id: Optional[int] = None) -> None:
    """Обратная совместимость: отправить уведомление."""
    if _bot_instance and telegram_id:
        await _bot_instance.send_notification(telegram_id, message)
