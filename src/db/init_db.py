import sqlite3
import os
from config import settings

DB_PATH = settings.db_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS processing_queue (
    chunk_id TEXT PRIMARY KEY,
    source_text TEXT,
    metadata JSON,
    status TEXT DEFAULT 'PENDING',  -- PENDING, PROCESSING, COMPLETED, FAILED
    retry_count INTEGER DEFAULT 0,
    output_json TEXT,
    verification_score REAL,
    error_log TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    filename TEXT PRIMARY KEY,
    status TEXT DEFAULT 'LIBRARY', -- LIBRARY, BUFFER, PROCESSING, COMPLETED
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db():
    print(f"Initializing database at: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        # Enable WAL mode for concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        cursor.executescript(SCHEMA)
        conn.commit()
        print("Database schema initialized successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
