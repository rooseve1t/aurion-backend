from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app, FOUNDER_EMAIL, FOUNDER_PASSWORD


def _auth_header(client: TestClient) -> dict[str, str]:
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    username = f"user_{uuid.uuid4().hex[:6]}"
    password = "Test12345!"
    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    assert register.status_code == 200
    login = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    access = login.json()["access_token"]
    return {"Authorization": f"Bearer {access}"}


def test_voice_preferences_and_preview() -> None:
    client = TestClient(app)
    headers = _auth_header(client)
    update = client.put("/api/v1/profile/preferences/voice", json={"persona": "jarvis"}, headers=headers)
    assert update.status_code == 200
    assert update.json()["voice_persona"] == "jarvis"

    preview = client.post(
        "/api/v1/voice/preview",
        json={"text": "Проверка голоса", "persona": "jarvis"},
        headers=headers,
    )
    assert preview.status_code == 200
    payload = preview.json()
    assert payload["voice_persona"] == "jarvis"
    assert payload["text"].startswith("Анализ завершён.")


def test_proactive_and_diy_and_guardian() -> None:
    client = TestClient(app)
    headers = _auth_header(client)

    proactive = client.post("/api/v1/proactive/generate", json={"lookback_days": 30}, headers=headers)
    assert proactive.status_code == 200
    assert proactive.json()["generated"] >= 1

    diy = client.post(
        "/api/v1/diy/sketches",
        json={
            "name": "ESP Lamp",
            "device_type": "light",
            "board": "ESP8266",
            "protocol": "mqtt",
            "sketch_code": "void setup(){} void loop(){}",
        },
        headers=headers,
    )
    assert diy.status_code == 200

    guardian = client.post(
        "/api/v1/guardian/scan",
        json={"hosts": ["127.0.0.1"], "ports": [22, 80, 443]},
        headers=headers,
    )
    assert guardian.status_code == 200
    assert guardian.json()["scanned_hosts"] == 1


def test_quantum_route_fallback() -> None:
    client = TestClient(app)
    headers = _auth_header(client)
    response = client.post(
        "/api/v1/quantum/route",
        json={"task_type": "simulation", "payload": {"n": 8}, "preferred_backend": "auto"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["backend"] in {"local-mvp", "hpc-lumi", "quantum-rings"}


def test_founder_can_login_without_registration() -> None:
    client = TestClient(app)
    login = client.post(
        "/api/v1/auth/token",
        data={"username": FOUNDER_EMAIL, "password": FOUNDER_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == FOUNDER_EMAIL
    assert me.json()["role"] == "creator"
