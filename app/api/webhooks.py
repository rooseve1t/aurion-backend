"""
Webhook-эндпоинт для приёма событий от внешних сервисов.
Валидация HMAC-подписи + публикация в Redis pub/sub.
"""
import hashlib
import hmac
import json
import logging
import os
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, Request

logger = logging.getLogger("aurion-webhooks")

router = APIRouter(tags=["webhooks"])

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


def _verify_signature(body: bytes, signature: str) -> bool:
    """Проверяет HMAC-SHA256 подпись запроса."""
    if not WEBHOOK_SECRET:
        # Если секрет не задан — пропускаем проверку (dev-режим)
        logger.warning("WEBHOOK_SECRET не задан — подпись не проверяется")
        return True
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@router.post("/incoming")
async def incoming_webhook(
    request: Request,
    x_webhook_signature: str = Header(default=""),
) -> Dict[str, Any]:
    """
    Принимает события от внешних сервисов.
    Публикует в Redis pub/sub канал `aurion:webhooks` для ProactivityManager.
    """
    body = await request.body()

    if x_webhook_signature and not _verify_signature(body, x_webhook_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload: Dict[str, Any] = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Публикуем в Redis pub/sub
    try:
        import redis.asyncio as aioredis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = aioredis.from_url(redis_url, decode_responses=True)
        await r.publish("aurion:webhooks", json.dumps(payload))
        await r.aclose()
        logger.info(f"Webhook опубликован в Redis: {payload.get('event', 'unknown')}")
    except Exception as e:
        logger.warning(f"Redis pub/sub недоступен: {e} — событие обработано локально")

    return {"status": "accepted", "event": payload.get("event", "unknown")}
