import os
import sqlite3

DB_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notifications.db")

def init_db():
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            original TEXT,
            ai TEXT,
            client TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_notification(timestamp, original, ai, client):
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO notifications (timestamp, original, ai, client)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, original, ai, client))
    conn.commit()
    conn.close()

def get_notifications(limit=20, date_filter=""):
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    if date_filter:
        c.execute('''
            SELECT timestamp, original, ai, client FROM notifications
            WHERE timestamp LIKE ?
            ORDER BY id DESC LIMIT ?
        ''', (date_filter + "%", limit))
    else:
        c.execute('''
            SELECT timestamp, original, ai, client FROM notifications
            ORDER BY id DESC LIMIT ?
        ''', (limit,))
    rows = c.fetchall()
    conn.close()
    notifs = []
    for row in rows:
        notifs.append({"timestamp": row[0], "original": row[1], "ai": row[2], "client": row[3]})
    return notifs

init_db()
