import sqlite3
import json
import os
from datetime import datetime
from config import settings

class DBManager:
    def __init__(self, db_path=None):
        self.db_path = str(db_path) if db_path else str(settings.db_path)

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def insert_chunk(self, chunk_id, source_text, metadata, notebook, filename):
        """
        Inserts a new chunk into the processing_queue.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO processing_queue (chunk_id, notebook, filename, source_text, metadata, status)
                VALUES (?, ?, ?, ?, ?, 'PENDING')
                ON CONFLICT(chunk_id) DO UPDATE SET
                    source_text=excluded.source_text,
                    metadata=excluded.metadata,
                    status='PENDING',
                    updated_at=CURRENT_TIMESTAMP
            """, (chunk_id, notebook, filename, source_text, json.dumps(metadata)))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def get_pending_chunk(self, notebook):
        """
        Fetches the next PENDING chunk and marks it as PROCESSING.
        (Peek-Lock-Process logic)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE processing_queue 
                SET status = 'PROCESSING', updated_at = CURRENT_TIMESTAMP
                WHERE chunk_id = (
                    SELECT chunk_id FROM processing_queue 
                    WHERE notebook = ? AND status = 'PENDING' 
                    ORDER BY created_at ASC LIMIT 1
                )
                RETURNING chunk_id, source_text, metadata
            """, (notebook,))
            row = cursor.fetchone()
            conn.commit()
            if row:
                return {"chunk_id": row[0], "source_text": row[1], "metadata": json.loads(row[2])}
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def get_pending_count(self, notebook):
        """
        Returns the number of chunks currently in PENDING state.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM processing_queue WHERE notebook = ? AND status = 'PENDING'", (notebook,))
            count = cursor.fetchone()[0]
            return count
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return 0
        finally:
            conn.close()

    def get_all_pending_chunks(self, notebook):
        """
        Returns all chunks currently in PENDING state.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT chunk_id, source_text, metadata 
                FROM processing_queue 
                WHERE notebook = ? AND status = 'PENDING'
            """, (notebook,))
            rows = cursor.fetchall()
            return [{"chunk_id": row[0], "source_text": row[1], "metadata": json.loads(row[2])} for row in rows]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def update_chunk_status(self, chunk_id, status, output_json=None, error_log=None, verification_score=None, notebook=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE processing_queue 
                SET status = ?, output_json = ?, error_log = ?, verification_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE chunk_id = ?
            """, (status, output_json, error_log, verification_score, chunk_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def add_document_to_library(self, filename, notebook):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO documents (notebook, filename, status) VALUES (?, ?, 'LIBRARY')", (notebook, filename))
            conn.commit()
        finally:
            conn.close()

    def get_documents_by_status(self, status, notebook):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT filename FROM documents WHERE notebook = ? AND status = ?", (notebook, status))
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_document_status(self, filename, notebook):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status FROM documents WHERE notebook = ? AND filename = ?", (notebook, filename))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def update_document_status(self, filename, status, notebook):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE documents SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE notebook = ? AND filename = ?", (status, notebook, filename))
            conn.commit()
        finally:
            conn.close()
