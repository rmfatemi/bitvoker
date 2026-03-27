import os
import time

from bitvoker.auth import (
    get_credentials,
    is_auth_enabled,
    verify_credentials,
    create_token,
    verify_token,
)


class TestGetCredentials:
    def test_returns_env_vars(self, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "secret")
        assert get_credentials() == ("admin", "secret")

    def test_returns_empty_when_not_set(self, monkeypatch):
        monkeypatch.delenv("BITVOKER_USERNAME", raising=False)
        monkeypatch.delenv("BITVOKER_PASSWORD", raising=False)
        assert get_credentials() == ("", "")


class TestIsAuthEnabled:
    def test_enabled_when_both_set(self, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "pass")
        assert is_auth_enabled() is True

    def test_disabled_when_username_missing(self, monkeypatch):
        monkeypatch.delenv("BITVOKER_USERNAME", raising=False)
        monkeypatch.setenv("BITVOKER_PASSWORD", "pass")
        assert is_auth_enabled() is False

    def test_disabled_when_password_missing(self, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.delenv("BITVOKER_PASSWORD", raising=False)
        assert is_auth_enabled() is False


class TestVerifyCredentials:
    def test_valid_credentials(self, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "secret")
        assert verify_credentials("admin", "secret") is True

    def test_invalid_password(self, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "secret")
        assert verify_credentials("admin", "wrong") is False

    def test_invalid_username(self, monkeypatch):
        monkeypatch.setenv("BITVOKER_USERNAME", "admin")
        monkeypatch.setenv("BITVOKER_PASSWORD", "secret")
        assert verify_credentials("wrong", "secret") is False

    def test_no_credentials_set(self, monkeypatch):
        monkeypatch.delenv("BITVOKER_USERNAME", raising=False)
        monkeypatch.delenv("BITVOKER_PASSWORD", raising=False)
        assert verify_credentials("admin", "secret") is False


class TestTokens:
    def test_create_and_verify_token(self):
        token = create_token("admin")
        assert verify_token(token) is True

    def test_invalid_token_format(self):
        assert verify_token("invalid") is False
        assert verify_token("") is False
        assert verify_token(None) is False

    def test_tampered_token(self):
        token = create_token("admin")
        parts = token.split(":")
        parts[2] = "tampered"
        assert verify_token(":".join(parts)) is False

    def test_expired_token(self, monkeypatch):
        token = create_token("admin")
        import bitvoker.auth as auth_module
        original_expiry = auth_module.TOKEN_EXPIRY
        auth_module.TOKEN_EXPIRY = -1
        assert verify_token(token) is False
        auth_module.TOKEN_EXPIRY = original_expiry
