"""
SQLite database module for Version 2 of the vocabulary system.

Extends the Version 1 schema with two new tables for spaced-repetition
scheduling and review history, while preserving all V1 tables and data.

Tables:
  - wrong_words     (V1: wrong-word notebook)
  - practice_stats  (V1: global practice statistics)
  - word_reviews    (V2: per-word spaced-repetition state)
  - review_log      (V2: history of every review event)

The database file is 'vocabulary_v2.db', kept separate from Version 1's
'vocabulary.db' to ensure data independence.
"""

import sqlite3
import os
from datetime import datetime

# Database file path — separate from Version 1 to keep data independent.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary_v2.db")


def get_connection():
    """Create and return a new SQLite connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialise the database by creating all tables if they do not already exist.
    Uses CREATE TABLE IF NOT EXISTS for safe, non-destructive migrations.
    This function is safe to call multiple times and never deletes existing data.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # ---- V1 tables (preserved exactly) ----
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                incorrect_answers INTEGER DEFAULT 0,
                updated_at TEXT
            )
        """)

        # ---- V2 new tables ----

        # Per-word spaced-repetition state.
        # One row per vocabulary word (PK = word).
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS word_reviews (
                word TEXT PRIMARY KEY,
                mastery_level TEXT DEFAULT 'unlearned',
                consecutive_correct INTEGER DEFAULT 0,
                review_interval_days INTEGER DEFAULT 0,
                ease_factor REAL DEFAULT 2.5,
                last_reviewed TEXT,
                next_review TEXT,
                total_reviews INTEGER DEFAULT 0,
                total_correct INTEGER DEFAULT 0,
                total_incorrect INTEGER DEFAULT 0
            )
        """)

        # Review history log — one row per review event.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                was_correct INTEGER NOT NULL,
                quality INTEGER,
                review_time TEXT NOT NULL,
                interval_before INTEGER,
                interval_after INTEGER,
                mastery_before TEXT,
                mastery_after TEXT,
                error_category TEXT
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


# ===========================================================================
# V1 functions (preserved from Version 1, unchanged)
# ===========================================================================

def record_wrong_word(word, student_answer, correct_answer, error_category):
    """Record or update a wrong-word entry (V1 preserved)."""
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
    """Return all wrong-word entries, most recent first (V1 preserved)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wrong_words ORDER BY last_mistake_time DESC")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_wrong_word_by_id(word_id):
    """Return a single wrong-word entry by ID, or None (V1 preserved)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wrong_words WHERE id = ?", (word_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_wrong_word(word_id):
    """Delete a wrong-word entry by ID. Returns True if deleted (V1 preserved)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wrong_words WHERE id = ?", (word_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def clear_wrong_words():
    """Remove all entries from the wrong-word notebook (V1 preserved)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wrong_words")
        conn.commit()
    finally:
        conn.close()


def update_practice_stats(total_delta, correct_delta, incorrect_delta):
    """Increment global practice statistics (V1 preserved)."""
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
    """Return the current practice statistics as a dict (V1 preserved)."""
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
    """Return the number of distinct words in the wrong-word notebook (V1 preserved)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM wrong_words")
        return cursor.fetchone()["cnt"]
    finally:
        conn.close()


def reset_all_data():
    """Clear all data including V2 tables (for testing / fresh start)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wrong_words")
        cursor.execute("DELETE FROM word_reviews")
        cursor.execute("DELETE FROM review_log")
        cursor.execute("""
            UPDATE practice_stats
            SET total_questions = 0, correct_answers = 0, incorrect_answers = 0, updated_at = ?
            WHERE id = 1
        """, (datetime.now().isoformat(),))
        conn.commit()
    finally:
        conn.close()


# ===========================================================================
# V2 new functions — spaced repetition & review tracking
# ===========================================================================

def get_word_review(word):
    """
    Return the review state for a word, or None if the word has never been
    reviewed (no row in word_reviews).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM word_reviews WHERE word = ?", (word,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_word_reviews():
    """Return review states for all words that have been reviewed at least once."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM word_reviews")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def upsert_word_review(word, mastery_level, consecutive_correct, review_interval_days,
                       ease_factor, last_reviewed, next_review,
                       total_reviews, total_correct, total_incorrect):
    """
    Insert or update the review state for a word.
    Uses INSERT OR REPLACE to handle both new and existing rows.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO word_reviews
                (word, mastery_level, consecutive_correct, review_interval_days,
                 ease_factor, last_reviewed, next_review,
                 total_reviews, total_correct, total_incorrect)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (word, mastery_level, consecutive_correct, review_interval_days,
              ease_factor, last_reviewed, next_review,
              total_reviews, total_correct, total_incorrect))
        conn.commit()
    finally:
        conn.close()


def record_review_log(word, was_correct, quality, review_time,
                      interval_before, interval_after,
                      mastery_before, mastery_after, error_category=None):
    """Append a review event to the review_log table."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO review_log
                (word, was_correct, quality, review_time,
                 interval_before, interval_after, mastery_before, mastery_after, error_category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (word, 1 if was_correct else 0, quality, review_time,
              interval_before, interval_after, mastery_before, mastery_after, error_category))
        conn.commit()
    finally:
        conn.close()


def get_review_logs(limit=50):
    """Return recent review log entries, most recent first."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM review_log ORDER BY review_time DESC LIMIT ?
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_words_due_for_review(now=None):
    """
    Return review states for all words that are due for review
    (next_review <= now, or never reviewed).
    """
    if now is None:
        now = datetime.now()
    now_str = now.isoformat()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM word_reviews
            WHERE next_review <= ? OR next_review IS NULL
            ORDER BY next_review ASC
        """, (now_str,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_mastery_distribution():
    """
    Return a dict with counts of words in each mastery level.
    Only includes words that have been reviewed at least once.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mastery_level, COUNT(*) AS cnt
            FROM word_reviews
            GROUP BY mastery_level
        """)
        result = {"unlearned": 0, "learning": 0, "familiar": 0, "mastered": 0}
        for row in cursor.fetchall():
            result[row["mastery_level"]] = row["cnt"]
        return result
    finally:
        conn.close()


def get_words_by_mastery(mastery_level):
    """Return review states for all words at the given mastery level."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM word_reviews WHERE mastery_level = ?", (mastery_level,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_reviews_today(now=None):
    """Return count of reviews performed today."""
    if now is None:
        now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM review_log WHERE review_time >= ?", (today_start,))
        return cursor.fetchone()["cnt"]
    finally:
        conn.close()


def get_weak_words(limit=10):
    """
    Return the weakest words (highest error rate among reviewed words).
    Weakness = total_incorrect / total_reviews, sorted descending.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM word_reviews
            WHERE total_reviews > 0
            ORDER BY (CAST(total_incorrect AS REAL) / total_reviews) DESC,
                     total_incorrect DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_recent_accuracy_trend(days=7, now=None):
    """
    Return daily accuracy for the last N days.
    Returns a list of dicts: [{date, total, correct, accuracy}, ...]
    """
    if now is None:
        now = datetime.now()
    from datetime import timedelta as _td
    conn = get_connection()
    try:
        cursor = conn.cursor()
        trend = []
        for i in range(days - 1, -1, -1):
            day = now - _td(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start.replace(hour=23, minute=59, second=59)
            cursor.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(was_correct) AS correct
                FROM review_log
                WHERE review_time >= ? AND review_time <= ?
            """, (day_start.isoformat(), day_end.isoformat()))
            row = cursor.fetchone()
            total = row["total"] or 0
            correct = row["correct"] or 0
            acc = round(correct / total * 100, 1) if total > 0 else 0.0
            trend.append({
                "date": day_start.strftime("%m-%d"),
                "total": total,
                "correct": correct,
                "accuracy": acc,
            })
        return trend
    finally:
        conn.close()


def timedelta_days(n):
    """Helper: return a datetime n days before now."""
    from datetime import timedelta
    return datetime.now() - timedelta(days=n)


def remove_wrong_word_if_mastered(word):
    """
    Remove a word from the wrong-word notebook if it has reached 'mastered' level.
    Returns True if the word was removed, False otherwise.
    """
    review = get_word_review(word)
    if review and review["mastery_level"] == "mastered":
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM wrong_words WHERE word = ?", (word,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    return False


def get_wrong_words_by_category(category):
    """Return wrong-word entries filtered by error category."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM wrong_words WHERE error_category = ? ORDER BY last_mistake_time DESC",
            (category,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
