"""
Smoke-тесты для MultiDeviceVoice.
"""
import pytest
from app.services.multi_device_voice import (
    MultiDeviceVoice,
    DevicePriority,
    DeviceStatus,
    get_multi_device_voice,
)


def test_get_multi_device_voice_singleton():
    m1 = get_multi_device_voice()
    m2 = get_multi_device_voice()
    assert m1 is m2


def test_multi_device_voice_instantiation():
    mdv = MultiDeviceVoice()
    assert mdv is not None
    assert mdv._redis is None
    assert mdv._ws_manager is None


def test_set_redis():
    mdv = MultiDeviceVoice()
    mdv.set_redis("fake_redis")
    assert mdv._redis == "fake_redis"


def test_set_ws_manager():
    mdv = MultiDeviceVoice()
    mdv.set_ws_manager("fake_ws")
    assert mdv._ws_manager == "fake_ws"


def test_device_priority_order():
    assert DevicePriority.BLUETOOTH_HEADPHONES < DevicePriority.LOCAL_SPEAKER
    assert DevicePriority.LOCAL_SPEAKER < DevicePriority.IPHONE_PUSH
    assert DevicePriority.IPHONE_PUSH < DevicePriority.BROWSER_FALLBACK


@pytest.mark.asyncio
async def test_get_available_devices_no_redis():
    """get_available_devices без Redis — browser_fallback всегда доступен."""
    mdv = MultiDeviceVoice()
    devices = await mdv.get_available_devices("user1")
    assert len(devices) == 4
    browser = next(d for d in devices if d.device_id == "browser_fallback")
    assert browser.available is True


@pytest.mark.asyncio
async def test_speak_fallback_no_redis():
    """speak без Redis и ws_manager — возвращает browser_fallback."""
    mdv = MultiDeviceVoice()
    result = await mdv.speak("Привет", "user1")
    assert result == "browser_fallback"


@pytest.mark.asyncio
async def test_check_bluetooth_no_redis():
    mdv = MultiDeviceVoice()
    result = await mdv._check_bluetooth("user1")
    assert result is False


@pytest.mark.asyncio
async def test_check_local_speaker_no_redis():
    mdv = MultiDeviceVoice()
    result = await mdv._check_local_speaker("user1")
    assert result is False
