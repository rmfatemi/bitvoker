import sqlite3

import pytest

from bitvoker.database import init_db, insert_notification, get_notifications


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    import bitvoker.database as db_module
    monkeypatch.setattr(db_module, "DB_FILENAME", str(db_path))
    init_db()
    return str(db_path)


class TestDatabase:
    def test_init_db_creates_table(self, test_db):
        conn = sqlite3.connect(test_db)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_insert_and_get_notification(self, test_db):
        insert_notification("2025-01-01 12:00:00", "test message", "ai result", "127.0.0.1")
        results = get_notifications(limit=10)
        assert len(results) == 1
        assert results[0]["original"] == "test message"
        assert results[0]["ai"] == "ai result"
        assert results[0]["client"] == "127.0.0.1"

    def test_get_notifications_with_limit(self, test_db):
        for i in range(5):
            insert_notification(f"2025-01-0{i + 1} 12:00:00", f"msg {i}", "", "127.0.0.1")
        results = get_notifications(limit=3)
        assert len(results) == 3

    def test_get_notifications_with_date_filter(self, test_db):
        insert_notification("2025-01-01 12:00:00", "old", "", "127.0.0.1")
        insert_notification("2025-06-15 12:00:00", "new", "", "127.0.0.1")
        results = get_notifications(limit=10, start_date="2025-06-01")
        assert len(results) == 1
        assert results[0]["original"] == "new"

    def test_get_notifications_empty(self, test_db):
        results = get_notifications(limit=10)
        assert results == []

    def test_multiple_inserts(self, test_db):
        for i in range(10):
            insert_notification(f"2025-01-01 12:{i:02d}:00", f"message {i}", "", "10.0.0.1")
        results = get_notifications(limit=100)
        assert len(results) == 10
