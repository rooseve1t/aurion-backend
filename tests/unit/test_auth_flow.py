"""
Pytest-тесты для auth flow: регистрация, логин, refresh, logout, blacklist.
Требования: 5.1, 5.2, 5.3, 5.4
"""
import uuid
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


def unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:10]}@example.com"


# ─── Регистрация ──────────────────────────────────────────────────────────────

class TestRegister:
    def test_register_success(self, client):
        """Новый пользователь регистрируется, получает access + refresh токены."""
        resp = client.post("/api/v1/auth/register", json={
            "email": unique_email(),
            "username": f"u_{uuid.uuid4().hex[:6]}",
            "password": "StrongPass1!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client):
        """Повторная регистрация с тем же email → 400."""
        email = unique_email()
        payload = {"email": email, "username": f"u_{uuid.uuid4().hex[:6]}", "password": "StrongPass1!"}
        client.post("/api/v1/auth/register", json=payload)
        resp = client.post("/api/v1/auth/register", json={**payload, "username": f"u_{uuid.uuid4().hex[:6]}"})
        assert resp.status_code in (400, 409)

    def test_register_invalid_email(self, client):
        """Невалидный email → 422."""
        resp = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "username": "someuser",
            "password": "StrongPass1!",
        })
        assert resp.status_code == 422


# ─── Логин ───────────────────────────────────────────────────────────────────

class TestLogin:
    @pytest.fixture(autouse=True)
    def _register(self, client):
        self.email = unique_email()
        self.password = "LoginPass99!"
        client.post("/api/v1/auth/register", json={
            "email": self.email,
            "username": f"u_{uuid.uuid4().hex[:6]}",
            "password": self.password,
        })

    def test_login_success(self, client):
        """Верные credentials → 200 + токены."""
        resp = client.post("/api/v1/auth/login", json={
            "email": self.email,
            "password": self.password,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client):
        """Неверный пароль → 401."""
        resp = client.post("/api/v1/auth/login", json={
            "email": self.email,
            "password": "WrongPassword!",
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        """Несуществующий email → 401."""
        resp = client.post("/api/v1/auth/login", json={
            "email": unique_email(),
            "password": "AnyPass1!",
        })
        assert resp.status_code == 401


# ─── Refresh ─────────────────────────────────────────────────────────────────

class TestRefresh:
    @pytest.fixture(autouse=True)
    def _tokens(self, client):
        email = unique_email()
        password = "RefreshPass1!"
        client.post("/api/v1/auth/register", json={
            "email": email,
            "username": f"u_{uuid.uuid4().hex[:6]}",
            "password": password,
        })
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]

    def test_refresh_returns_new_access_token(self, client):
        """Валидный refresh_token → новый access_token."""
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": self.refresh_token})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["access_token"] != self.access_token

    def test_refresh_invalid_token(self, client):
        """Невалидный refresh_token → 401."""
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.token.here"})
        assert resp.status_code == 401


# ─── Logout + blacklist ───────────────────────────────────────────────────────

class TestLogout:
    @pytest.fixture(autouse=True)
    def _tokens(self, client):
        email = unique_email()
        password = "LogoutPass1!"
        client.post("/api/v1/auth/register", json={
            "email": email,
            "username": f"u_{uuid.uuid4().hex[:6]}",
            "password": password,
        })
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        data = resp.json()
        self.access_token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def test_logout_success(self, client):
        """Logout с валидным токеном → 200."""
        resp = client.post("/api/v1/auth/logout", headers=self.headers)
        assert resp.status_code == 200

    def test_revoked_token_rejected(self, client):
        """После logout повторный запрос с тем же токеном → 401."""
        client.post("/api/v1/auth/logout", headers=self.headers)
        resp = client.get("/api/v1/auth/me", headers=self.headers)
        assert resp.status_code == 401

    def test_me_requires_auth(self, client):
        """GET /me без токена → 401."""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_with_valid_token(self, client):
        """GET /me с валидным токеном → 200 + email."""
        resp = client.get("/api/v1/auth/me", headers=self.headers)
        assert resp.status_code == 200
        assert "email" in resp.json()
