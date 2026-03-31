"""
EncryptionService — AES-256-GCM шифрование чувствительных данных.

Ключ читается из переменной окружения ENCRYPTION_KEY (32 байта в hex).
Если ключ не задан — генерируется временный (только для разработки).

Формат зашифрованных данных: nonce(12) + ciphertext+tag
"""
import logging
import os
import secrets
from typing import Optional

logger = logging.getLogger("aurion-encryption")

_KEY: Optional[bytes] = None


def _get_key() -> bytes:
    global _KEY
    if _KEY is not None:
        return _KEY

    raw = os.getenv("ENCRYPTION_KEY", "")
    if raw:
        try:
            key = bytes.fromhex(raw)
            if len(key) == 32:
                _KEY = key
                return _KEY
            logger.warning("ENCRYPTION_KEY должен быть 32-байтным hex. Генерирую временный ключ.")
        except ValueError:
            logger.warning("ENCRYPTION_KEY невалидный hex. Генерирую временный ключ.")

    logger.warning(
        "ENCRYPTION_KEY не задан — используется временный ключ. "
        "Данные не будут расшифрованы после перезапуска!"
    )
    _KEY = secrets.token_bytes(32)
    return _KEY


def encrypt_aes256(data: bytes) -> bytes:
    """Зашифровать данные AES-256-GCM. Возвращает nonce(12) + ciphertext+tag."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        raise RuntimeError("Пакет 'cryptography' не установлен.")

    key = _get_key()
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(key)
    ct_with_tag = aesgcm.encrypt(nonce, data, None)
    return nonce + ct_with_tag


def decrypt_aes256(data: bytes) -> bytes:
    """Расшифровать данные AES-256-GCM. Ожидает nonce(12) + ciphertext+tag."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        raise RuntimeError("Пакет 'cryptography' не установлен.")

    if len(data) < 28:
        raise ValueError("Данные слишком короткие для расшифровки.")

    key = _get_key()
    nonce = data[:12]
    ct_with_tag = data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct_with_tag, None)


def encrypt_str(text: str) -> bytes:
    """Зашифровать строку UTF-8."""
    return encrypt_aes256(text.encode("utf-8"))


def decrypt_str(data: bytes) -> str:
    """Расшифровать строку UTF-8."""
    return decrypt_aes256(data).decode("utf-8")


def reset_key() -> None:
    """Сбросить кэшированный ключ (для тестов)."""
    global _KEY
    _KEY = None
