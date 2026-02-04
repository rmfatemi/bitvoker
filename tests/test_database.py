"""Unit tests for database.py module."""

import os
import sqlite3
import tempfile
import pytest
from unittest.mock import patch
from bitvoker import database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    with patch("bitvoker.database.DB_FILENAME", path):
        database.init_db()
        yield path
    if os.path.exists(path):
        os.remove(path)


class TestDatabase:
    """Test cases for database functions."""

    def test_init_db(self, temp_db):
        """Test database initialization."""
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        result = c.fetchone()
        conn.close()
        assert result is not None

    def test_insert_notification(self, temp_db):
        """Test inserting a notification."""
        with patch("bitvoker.database.DB_FILENAME", temp_db):
            database.insert_notification("2024-01-01 12:00:00", "Original message", "AI processed", "192.168.1.1")

        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT * FROM notifications")
        result = c.fetchone()
        conn.close()

        assert result is not None
        assert result[1] == "2024-01-01 12:00:00"
        assert result[2] == "Original message"
        assert result[3] == "AI processed"
        assert result[4] == "192.168.1.1"

    def test_get_notifications_empty(self, temp_db):
        """Test getting notifications from empty database."""
        with patch("bitvoker.database.DB_FILENAME", temp_db):
            notifications = database.get_notifications()
        assert notifications == []

    def test_get_notifications_with_limit(self, temp_db):
        """Test getting notifications with limit."""
        with patch("bitvoker.database.DB_FILENAME", temp_db):
            for i in range(5):
                database.insert_notification(f"2024-01-01 12:00:0{i}", f"Message {i}", f"AI {i}", "192.168.1.1")
            notifications = database.get_notifications(limit=3)
        assert len(notifications) == 3

    def test_get_notifications_order(self, temp_db):
        """Test that notifications are returned in descending order."""
        with patch("bitvoker.database.DB_FILENAME", temp_db):
            database.insert_notification("2024-01-01 12:00:00", "First message", "AI 1", "192.168.1.1")
            database.insert_notification("2024-01-01 12:00:01", "Second message", "AI 2", "192.168.1.1")
            notifications = database.get_notifications()

        assert len(notifications) == 2
        assert notifications[0]["original"] == "Second message"
        assert notifications[1]["original"] == "First message"

    def test_get_notifications_with_date_filter(self, temp_db):
        """Test getting notifications with date filters."""
        with patch("bitvoker.database.DB_FILENAME", temp_db):
            database.insert_notification("2024-01-01 12:00:00", "Message 1", "AI 1", "192.168.1.1")
            database.insert_notification("2024-01-02 12:00:00", "Message 2", "AI 2", "192.168.1.1")
            database.insert_notification("2024-01-03 12:00:00", "Message 3", "AI 3", "192.168.1.1")

            notifications = database.get_notifications(start_date="2024-01-02", end_date="2024-01-02")

        assert len(notifications) == 1
        assert notifications[0]["original"] == "Message 2"

    def test_get_notifications_format(self, temp_db):
        """Test that notifications are returned in correct format."""
        with patch("bitvoker.database.DB_FILENAME", temp_db):
            database.insert_notification("2024-01-01 12:00:00", "Original", "AI", "192.168.1.1")
            notifications = database.get_notifications()

        assert len(notifications) == 1
        notification = notifications[0]
        assert "timestamp" in notification
        assert "original" in notification
        assert "ai" in notification
        assert "client" in notification
