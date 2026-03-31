"""
Unit-тесты для app/api/profile.py — export и delete endpoints.
Требования: 6.4, 6.5
"""
import uuid
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main_final import app
    return TestClient(app)


def _register_and_login(client: TestClient) -> dict:
    """Регистрирует нового пользователя и возвращает токены."""
    email = f"profile_{uuid.uuid4().hex[:8]}@test.com"
    password = "ProfilePass1!"
    username = f"u_{uuid.uuid4().hex[:6]}"

    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
    })
    assert reg.status_code == 200, reg.text
    data = reg.json()
    return {
        "access_token": data["access_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
    }


class TestExportEndpoint:
    def test_export_requires_auth(self, client):
        """GET /api/v2/profile/export без токена — 401."""
        resp = client.get("/api/v2/profile/export")
        assert resp.status_code == 401

    def test_export_returns_200(self, client):
        """GET /api/v2/profile/export с токеном — 200."""
        tokens = _register_and_login(client)
        resp = client.get("/api/v2/profile/export", headers=tokens["headers"])
        assert resp.status_code == 200

    def test_export_structure(self, client):
        """Ответ содержит обязательные поля."""
        tokens = _register_and_login(client)
        resp = client.get("/api/v2/profile/export", headers=tokens["headers"])
        data = resp.json()
        assert "user_id" in data
        assert "email" in data
        assert "feed_cards" in data
        assert "subscriptions" in data
        assert "memory" in data
        assert "evolution_proposals" in data

    def test_export_lists_are_lists(self, client):
        """feed_cards, subscriptions, memory, evolution_proposals — списки."""
        tokens = _register_and_login(client)
        resp = client.get("/api/v2/profile/export", headers=tokens["headers"])
        data = resp.json()
        assert isinstance(data["feed_cards"], list)
        assert isinstance(data["subscriptions"], list)
        assert isinstance(data["memory"], list)
        assert isinstance(data["evolution_proposals"], list)

    def test_export_user_isolation(self, client):
        """Два разных пользователя получают разные user_id в экспорте."""
        t1 = _register_and_login(client)
        t2 = _register_and_login(client)
        r1 = client.get("/api/v2/profile/export", headers=t1["headers"]).json()
        r2 = client.get("/api/v2/profile/export", headers=t2["headers"]).json()
        assert r1["user_id"] != r2["user_id"]


class TestDeleteEndpoint:
    def test_delete_requires_auth(self, client):
        """DELETE /api/v2/profile без токена — 401."""
        resp = client.delete("/api/v2/profile")
        assert resp.status_code == 401

    def test_delete_returns_202(self, client):
        """DELETE /api/v2/profile с токеном — 202 Accepted."""
        tokens = _register_and_login(client)
        resp = client.delete("/api/v2/profile", headers=tokens["headers"])
        assert resp.status_code == 202

    def test_delete_response_structure(self, client):
        """Ответ содержит message, user_id, scheduled_deletion_hours."""
        tokens = _register_and_login(client)
        resp = client.delete("/api/v2/profile", headers=tokens["headers"])
        data = resp.json()
        assert "message" in data
        assert "user_id" in data
        assert data.get("scheduled_deletion_hours") == 24

    def test_delete_deactivates_account(self, client):
        """После DELETE аккаунт деактивирован — повторный запрос возвращает 401 или 403."""
        tokens = _register_and_login(client)
        client.delete("/api/v2/profile", headers=tokens["headers"])
        resp = client.get("/api/v2/profile/export", headers=tokens["headers"])
        assert resp.status_code in (401, 403)
