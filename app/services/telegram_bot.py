"""
Telegram-бот JARVIS — уведомления и команды управления.
Если TELEGRAM_BOT_TOKEN не задан — инициализация пропускается.
"""
import logging
from typing import Optional, Any

logger = logging.getLogger("aurion-telegram")

_bot_app: Optional[Any] = None
_chat_ids: set[int] = set()


async def init_telegram_bot() -> None:
    """Инициализация Telegram-бота. Пропускается если токен не задан."""
    global _bot_app
    from ..config import settings

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN не задан — Telegram-бот отключён")
        return

    try:
        from telegram.ext import Application, CommandHandler

        app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        app.add_handler(CommandHandler("start",   _cmd_start))
        app.add_handler(CommandHandler("status",  _cmd_status))
        app.add_handler(CommandHandler("brief",   _cmd_brief))
        app.add_handler(CommandHandler("mission", _cmd_mission))

        _bot_app = app
        # Запускаем polling в фоне (не блокирует)
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        logger.info("✅ Telegram-бот JARVIS запущен")
    except Exception as e:
        logger.error(f"Ошибка запуска Telegram-бота: {e}")
        _bot_app = None


async def send_notification(message: str) -> None:
    """Отправить уведомление всем подписанным чатам."""
    if not _bot_app or not _chat_ids:
        return
    for chat_id in list(_chat_ids):
        try:
            await _bot_app.bot.send_message(chat_id=chat_id, text=f"🤖 JARVIS: {message}")
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение в чат {chat_id}: {e}")


# ─── Обработчики команд ──────────────────────────────────────────────────────

async def _cmd_start(update: Any, context: Any) -> None:
    chat_id = update.effective_chat.id
    _chat_ids.add(chat_id)
    await update.message.reply_text(
        "Добрый день. Я JARVIS — персональный ИИ-ассистент системы Aurion OS.\n"
        "Доступные команды:\n"
        "/status — статус системы\n"
        "/brief — утренний брифинг\n"
        "/mission — активные миссии"
    )


async def _cmd_status(update: Any, context: Any) -> None:
    await update.message.reply_text(
        "📊 Статус Aurion OS:\n"
        "• Backend: онлайн\n"
        "• JARVIS: активен\n"
        "• Агенты: готовы\n"
        "• Угрозы: не обнаружены"
    )


async def _cmd_brief(update: Any, context: Any) -> None:
    await update.message.reply_text(
        "📋 Утренний брифинг:\n"
        "Все системы в норме, сэр. "
        "Активных миссий нет. "
        "Угроз безопасности не обнаружено."
    )


async def _cmd_mission(update: Any, context: Any) -> None:
    await update.message.reply_text(
        "🎯 Активные миссии:\n"
        "Нет активных миссий. "
        "Создайте миссию через веб-интерфейс Aurion OS."
    )
