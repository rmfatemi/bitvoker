import pytest
from unittest.mock import MagicMock, patch

from bitvoker.handler import Handler, TOKEN_PREFIX


class TestVerifyToken:
    def _make_handler(self, token=""):
        handler = object.__new__(Handler)
        handler.client_address = ("127.0.0.1", 12345)
        server = MagicMock()
        config = MagicMock()
        config.config_data = {"message_token": token}
        server.config = config
        handler.server = server
        return handler

    def test_no_token_configured_passes_through(self):
        handler = self._make_handler("")
        assert handler._verify_token("hello world") == "hello world"

    def test_valid_token(self):
        handler = self._make_handler("mysecret")
        assert handler._verify_token("TOKEN:mysecret:hello world") == "hello world"

    def test_invalid_token(self):
        handler = self._make_handler("mysecret")
        assert handler._verify_token("TOKEN:wrong:hello") is None

    def test_missing_token_prefix(self):
        handler = self._make_handler("mysecret")
        assert handler._verify_token("hello world") is None

    def test_malformed_token(self):
        handler = self._make_handler("mysecret")
        assert handler._verify_token("TOKEN:noseparator") is None

    def test_empty_message_after_token(self):
        handler = self._make_handler("mysecret")
        assert handler._verify_token("TOKEN:mysecret:") == ""

    def test_no_config_attribute(self):
        handler = object.__new__(Handler)
        handler.client_address = ("127.0.0.1", 12345)
        handler.server = MagicMock(spec=[])
        assert handler._verify_token("hello") == "hello"
