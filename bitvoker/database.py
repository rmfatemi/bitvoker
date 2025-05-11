import os
import sqlite3


DB_FILENAME = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "database.db")


def init_db():
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS notifications
              (
                  id        INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  original  TEXT,
                  ai        TEXT,
                  client    TEXT
              )
              """)
    conn.commit()
    conn.close()


def insert_notification(timestamp, original, ai, client):
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute(
        """
              INSERT INTO notifications (timestamp, original, ai, client)
              VALUES (?, ?, ?, ?)
              """,
        (timestamp, original, ai, client),
    )
    conn.commit()
    conn.close()


def get_notifications(limit=20, start_date="", end_date=""):
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()

    query = "SELECT timestamp, original, ai, client FROM notifications"
    filters = []
    params = []

    if start_date:
        filters.append("DATE(timestamp) >= DATE(?)")
        params.append(start_date)
    if end_date:
        filters.append("DATE(timestamp) <= DATE(?)")
        params.append(end_date)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    c.execute(query, tuple(params))
    rows = c.fetchall()
    conn.close()

    notifs = []
    for row in rows:
        notifs.append({"timestamp": row[0], "original": row[1], "ai": row[2], "client": row[3]})
    return notifs


init_db()
