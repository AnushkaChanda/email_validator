import sqlite3
from datetime import datetime

DB_NAME = "validations.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT NOT NULL,
            checked_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_validation(email: str, status: str, details_json: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO validation_logs (email, status, details, checked_at)
        VALUES (?, ?, ?, ?)
    """, (email, status, details_json, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
