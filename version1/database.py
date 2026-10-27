"""
SQLite database module for the vocabulary system.

Handles persistence of:
  - Wrong-word records (错词本)
  - Practice statistics (练习统计)

The database is initialised automatically on first use.
"""

import sqlite3
import os
from datetime import datetime

# Database file path — stored alongside this module.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary.db")


def get_connection():
    """Create and return a new SQLite connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialise the database by creating tables if they do not already exist.
    Also ensures a practice_stats row exists for accumulating global statistics.
    This function is safe to call multiple times.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Wrong-word notebook table.
        # The 'word' column has a UNIQUE constraint so that repeated mistakes
        # on the same word increment mistake_count instead of creating duplicates.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wrong_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                student_answer TEXT,
                correct_answer TEXT,
                error_category TEXT,
                mistake_count INTEGER DEFAULT 1,
                last_mistake_time TEXT
            )
        """)

        # Practice statistics table (single row, id = 1).
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                incorrect_answers INTEGER DEFAULT 0,
                updated_at TEXT
            )
        """)

        # Ensure the single stats row exists.
        cursor.execute("SELECT COUNT(*) FROM practice_stats WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO practice_stats (id, total_questions, correct_answers, incorrect_answers, updated_at)
                VALUES (1, 0, 0, 0, ?)
            """, (datetime.now().isoformat(),))

        conn.commit()
    finally:
        conn.close()


def record_wrong_word(word, student_answer, correct_answer, error_category):
    """
    Record or update a wrong-word entry.
    If the word already exists in the notebook, increment its mistake_count
    and update the latest answer / category / timestamp.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("SELECT id, mistake_count FROM wrong_words WHERE word = ?", (word,))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE wrong_words
                SET student_answer = ?, correct_answer = ?, error_category = ?,
                    mistake_count = ?, last_mistake_time = ?
                WHERE id = ?
            """, (student_answer, correct_answer, error_category,
                  row["mistake_count"] + 1, now, row["id"]))
        else:
            cursor.execute("""
                INSERT INTO wrong_words (word, student_answer, correct_answer, error_category, mistake_count, last_mistake_time)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (word, student_answer, correct_answer, error_category, now))

        conn.commit()
    finally:
        conn.close()


def get_wrong_words():
    """Return all wrong-word entries, ordered by last mistake time (most recent first)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM wrong_words ORDER BY last_mistake_time DESC
        """)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_wrong_word_by_id(word_id):
    """Return a single wrong-word entry by its database ID, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wrong_words WHERE id = ?", (word_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_wrong_word(word_id):
    """Delete a wrong-word entry by its database ID. Returns True if a row was deleted."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wrong_words WHERE id = ?", (word_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def clear_wrong_words():
    """Remove all entries from the wrong-word notebook."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wrong_words")
        conn.commit()
    finally:
        conn.close()


def update_practice_stats(total_delta, correct_delta, incorrect_delta):
    """
    Increment the global practice statistics by the given deltas.
    Typically total_delta = number of questions, correct_delta / incorrect_delta
    are the counts of correct / incorrect answers in one practice session.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE practice_stats
            SET total_questions = total_questions + ?,
                correct_answers = correct_answers + ?,
                incorrect_answers = incorrect_answers + ?,
                updated_at = ?
            WHERE id = 1
        """, (total_delta, correct_delta, incorrect_delta, now))
        conn.commit()
    finally:
        conn.close()


def get_practice_stats():
    """Return the current practice statistics as a dict."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM practice_stats WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {"total_questions": 0, "correct_answers": 0, "incorrect_answers": 0}
    finally:
        conn.close()


def get_wrong_word_count():
    """Return the number of distinct words in the wrong-word notebook."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM wrong_words")
        return cursor.fetchone()["cnt"]
    finally:
        conn.close()


def reset_all_data():
    """Clear all wrong-word records and reset practice statistics to zero."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wrong_words")
        cursor.execute("""
            UPDATE practice_stats
            SET total_questions = 0, correct_answers = 0, incorrect_answers = 0, updated_at = ?
            WHERE id = 1
        """, (datetime.now().isoformat(),))
        conn.commit()
    finally:
        conn.close()
