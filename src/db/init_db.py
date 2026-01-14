import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "study_engine.db")

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
"""

def init_db():
    print(f"Initializing database at: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(SCHEMA)
        conn.commit()
        print("Database schema initialized successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
