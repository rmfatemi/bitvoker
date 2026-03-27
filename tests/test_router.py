import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from bitvoker.api import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAuthEndpoints:
    def test_auth_status_disabled(self, client, monkeypatch):
        monkeypatch.delenv("BITVOKER_USERNAME", raising=False)
        monkeypatch.delenv("BITVOKER_PASSWORD", raising=False)
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        assert response.json()["enabled"] is False

    def test_auth_status_enabled(self, client, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "pass")
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        assert response.json()["enabled"] is True

    def test_login_success(self, client, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "pass")
        response = client.post("/api/auth/login", json={"username": "admin", "password": "pass"})
        assert response.status_code == 200
        assert "token" in response.json()

    def test_login_failure(self, client, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "pass")
        response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
        assert response.status_code == 401

    def test_login_when_auth_disabled(self, client, monkeypatch):
        monkeypatch.delenv("BITVOKER_USERNAME", raising=False)
        monkeypatch.delenv("BITVOKER_PASSWORD", raising=False)
        response = client.post("/api/auth/login", json={"username": "any", "password": "any"})
        assert response.status_code == 200


class TestProtectedEndpoints:
    def test_config_without_auth(self, client, monkeypatch):
        monkeypatch.delenv("BITVOKER_USERNAME", raising=False)
        monkeypatch.delenv("BITVOKER_PASSWORD", raising=False)
        response = client.get("/api/config")
        assert response.status_code == 200

    def test_config_with_auth_no_token(self, client, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "pass")
        response = client.get("/api/config")
        assert response.status_code == 401

    def test_config_with_valid_token(self, client, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "pass")
        login_resp = client.post("/api/auth/login", json={"username": "admin", "password": "pass"})
        token = login_resp.json()["token"]
        response = client.get("/api/config", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_notifications_without_auth(self, client, monkeypatch):
        monkeypatch.delenv("BITVOKER_USERNAME", raising=False)
        monkeypatch.delenv("BITVOKER_PASSWORD", raising=False)
        response = client.get("/api/notifications")
        assert response.status_code == 200

    def test_logs_without_auth(self, client, monkeypatch):
        monkeypatch.delenv("BITVOKER_USERNAME", raising=False)
        monkeypatch.delenv("BITVOKER_PASSWORD", raising=False)
        response = client.get("/api/logs")
        assert response.status_code == 200
