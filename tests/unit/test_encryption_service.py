"""
Unit-тесты для EncryptionService — AES-256-GCM шифрование.
Требования: 17.3
"""
import os
import secrets
import pytest


@pytest.fixture(autouse=True)
def reset_key():
    """Сбрасываем кэшированный ключ перед каждым тестом."""
    from app.services.encryption_service import reset_key as _reset
    _reset()
    yield
    _reset()


class TestEncryptDecrypt:
    def test_round_trip_bytes(self):
        """encrypt → decrypt возвращает исходные байты."""
        from app.services.encryption_service import encrypt_aes256, decrypt_aes256
        data = b"hello aurion"
        assert decrypt_aes256(encrypt_aes256(data)) == data

    def test_round_trip_empty(self):
        """Пустые байты шифруются и расшифровываются корректно."""
        from app.services.encryption_service import encrypt_aes256, decrypt_aes256
        assert decrypt_aes256(encrypt_aes256(b"")) == b""

    def test_round_trip_str(self):
        """encrypt_str → decrypt_str возвращает исходную строку."""
        from app.services.encryption_service import encrypt_str, decrypt_str
        text = "Привет, JARVIS!"
        assert decrypt_str(encrypt_str(text)) == text

    def test_ciphertext_differs_from_plaintext(self):
        """Зашифрованные данные не совпадают с исходными."""
        from app.services.encryption_service import encrypt_aes256
        data = b"secret data"
        assert encrypt_aes256(data) != data

    def test_nonce_randomness(self):
        """Два вызова encrypt дают разные результаты (разные nonce)."""
        from app.services.encryption_service import encrypt_aes256
        data = b"same data"
        ct1 = encrypt_aes256(data)
        ct2 = encrypt_aes256(data)
        assert ct1 != ct2

    def test_ciphertext_length(self):
        """Длина шифртекста = 12 (nonce) + len(data) + 16 (GCM tag)."""
        from app.services.encryption_service import encrypt_aes256
        data = b"test"
        ct = encrypt_aes256(data)
        assert len(ct) == 12 + len(data) + 16

    def test_decrypt_too_short_raises(self):
        """Слишком короткие данные вызывают ValueError."""
        from app.services.encryption_service import decrypt_aes256
        with pytest.raises(ValueError):
            decrypt_aes256(b"short")

    def test_decrypt_tampered_raises(self):
        """Изменённый шифртекст вызывает исключение (GCM integrity check)."""
        from app.services.encryption_service import encrypt_aes256, decrypt_aes256
        ct = bytearray(encrypt_aes256(b"important"))
        ct[-1] ^= 0xFF  # портим последний байт (тег)
        with pytest.raises(Exception):
            decrypt_aes256(bytes(ct))

    def test_explicit_key_used(self):
        """Явный 32-байтный hex-ключ используется корректно."""
        from app.services.encryption_service import reset_key, encrypt_aes256, decrypt_aes256
        key_hex = secrets.token_bytes(32).hex()
        os.environ["ENCRYPTION_KEY"] = key_hex
        reset_key()
        data = b"keyed data"
        assert decrypt_aes256(encrypt_aes256(data)) == data
        del os.environ["ENCRYPTION_KEY"]
