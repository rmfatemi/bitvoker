import pytest
from unittest.mock import MagicMock, patch

from bitvoker.notifier import Notifier


class TestNotifierSetup:
    def test_empty_destinations(self):
        notifier = Notifier([])
        assert len(notifier.apprise.servers) == 0

    def test_disabled_destination_skipped(self):
        notifier = Notifier([{"name": "test", "url": "json://localhost", "enabled": False}])
        assert len(notifier.apprise.servers) == 0

    def test_enabled_destination_added(self):
        notifier = Notifier([{"name": "test", "url": "json://localhost", "enabled": True}])
        assert len(notifier.apprise.servers) == 1

    def test_update_destinations(self):
        notifier = Notifier([])
        assert len(notifier.apprise.servers) == 0
        notifier.update_destinations([{"name": "new", "url": "json://localhost", "enabled": True}])
        assert len(notifier.apprise.servers) == 1


class TestNotifierSend:
    def test_send_with_no_servers(self):
        notifier = Notifier([])
        notifier.send_message("test message")

    def test_send_with_invalid_tags(self):
        notifier = Notifier([{"name": "test", "url": "json://localhost", "enabled": True}])
        notifier.send_message("test", destination_names=["nonexistent"])
