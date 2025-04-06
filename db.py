import sqlite3
import time
import uuid

DB_NAME = "smc_pro.db"
SESSION_DURATION = 900  # 15 minutos

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )''')
    conn.commit()
    conn.close()

def create_session(user):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    token = str(uuid.uuid4())
    timestamp = int(time.time())
    c.execute("INSERT INTO sessions (id, user, created_at) VALUES (?, ?, ?)",
              (token, user, timestamp))
    conn.commit()
    conn.close()
    return token

def validate_session(user=None, token=None, return_user=False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = int(time.time())

    if token:
        c.execute("SELECT user, created_at FROM sessions WHERE id = ?", (token,))
        row = c.fetchone()
        if not row:
            return (None, False)
        user_val, created_at = row
        if now - created_at > SESSION_DURATION:
            c.execute("DELETE FROM sessions WHERE id = ?", (token,))
            conn.commit()
            conn.close()
            return (user_val, False)
        conn.close()
        return (user_val, True)

    c.execute("SELECT COUNT(*) FROM sessions WHERE user = ? AND ? - created_at < ?",
              (user, now, SESSION_DURATION))
    count = c.fetchone()[0]
    conn.close()
    return count

def close_expired_sessions(user):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = int(time.time())
    c.execute("DELETE FROM sessions WHERE user = ? AND ? - created_at > ?",
              (user, now, SESSION_DURATION))
    conn.commit()
    conn.close()
