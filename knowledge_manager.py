
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "zilda.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_knowledge_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_knowledge(title, category, content):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO knowledge (title, category, content)
            VALUES (?, ?, ?)
            """,
            (title, category or "General", content)
        )
        return cursor.lastrowid


def get_all_knowledge():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM knowledge ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]


def delete_knowledge(article_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM knowledge WHERE id = ?",
            (article_id,)
        )
        return cursor.rowcount > 0


def search_knowledge(query, limit=5):
    query = (query or "").strip()

    if not query:
        return []

    pattern = f"%{query}%"

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM knowledge
            WHERE title LIKE ?
               OR content LIKE ?
               OR category LIKE ?
            ORDER BY id DESC
            LIMIT ?
        """, (pattern, pattern, pattern, limit)).fetchall()

        return [dict(row) for row in rows]


# Automatically create the database and table
initialize_knowledge_db()
