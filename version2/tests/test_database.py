"""
Tests for the V2 database module — spaced repetition persistence,
review logging, analytics queries, and targeted wrong-word practice.

These tests verify that scheduling information survives application restarts
(by closing and reopening the database connection).
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import database as db
from spaced_repetition import (
    compute_next_review,
    determine_mastery,
    DEFAULT_EASE_FACTOR,
    MASTERY_UNLEARNED,
    MASTERY_LEARNING,
    MASTERY_FAMILIAR,
    MASTERY_MASTERED,
)


class TestDatabaseV2(unittest.TestCase):
    """Tests for V2 database tables and functions."""

    def setUp(self):
        db.init_db()
        db.reset_all_data()

    def tearDown(self):
        db.reset_all_data()

    def test_word_review_insert_and_retrieve(self):
        """Insert a word review and retrieve it."""
        db.upsert_word_review(
            word="test_word", mastery_level=MASTERY_LEARNING,
            consecutive_correct=1, review_interval_days=1,
            ease_factor=2.5, last_reviewed=datetime.now().isoformat(),
            next_review=(datetime.now() + timedelta(days=1)).isoformat(),
            total_reviews=1, total_correct=1, total_incorrect=0,
        )
        review = db.get_word_review("test_word")
        self.assertIsNotNone(review)
        self.assertEqual(review["word"], "test_word")
        self.assertEqual(review["mastery_level"], MASTERY_LEARNING)
        self.assertEqual(review["consecutive_correct"], 1)

    def test_word_review_update(self):
        """Update an existing word review (INSERT OR REPLACE)."""
        db.upsert_word_review(
            word="test_word", mastery_level=MASTERY_LEARNING,
            consecutive_correct=1, review_interval_days=1,
            ease_factor=2.5, last_reviewed=datetime.now().isoformat(),
            next_review=(datetime.now() + timedelta(days=1)).isoformat(),
            total_reviews=1, total_correct=1, total_incorrect=0,
        )
        db.upsert_word_review(
            word="test_word", mastery_level=MASTERY_FAMILIAR,
            consecutive_correct=2, review_interval_days=3,
            ease_factor=2.5, last_reviewed=datetime.now().isoformat(),
            next_review=(datetime.now() + timedelta(days=3)).isoformat(),
            total_reviews=2, total_correct=2, total_incorrect=0,
        )
        review = db.get_word_review("test_word")
        self.assertEqual(review["mastery_level"], MASTERY_FAMILIAR)
        self.assertEqual(review["consecutive_correct"], 2)
        self.assertEqual(review["review_interval_days"], 3)

    def test_persistence_after_restart(self):
        """
        Verify that review data persists after simulating an application restart.
        We do this by writing data, then re-initialising the database (which
        should NOT destroy existing data), and reading it back.
        """
        db.upsert_word_review(
            word="persist_word", mastery_level=MASTERY_MASTERED,
            consecutive_correct=5, review_interval_days=15,
            ease_factor=2.6, last_reviewed=datetime.now().isoformat(),
            next_review=(datetime.now() + timedelta(days=15)).isoformat(),
            total_reviews=10, total_correct=8, total_incorrect=2,
        )
        # Simulate restart: re-init the database.
        db.init_db()
        review = db.get_word_review("persist_word")
        self.assertIsNotNone(review)
        self.assertEqual(review["mastery_level"], MASTERY_MASTERED)
        self.assertEqual(review["consecutive_correct"], 5)
        self.assertEqual(review["review_interval_days"], 15)
        self.assertAlmostEqual(review["ease_factor"], 2.6, places=1)
        self.assertEqual(review["total_reviews"], 10)

    def test_review_log(self):
        """Record review log entries and retrieve them."""
        now = datetime.now().isoformat()
        db.record_review_log(
            word="log_word", was_correct=True, quality=5,
            review_time=now, interval_before=1, interval_after=3,
            mastery_before=MASTERY_LEARNING, mastery_after=MASTERY_FAMILIAR,
        )
        logs = db.get_review_logs(limit=10)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["word"], "log_word")
        self.assertTrue(logs[0]["was_correct"])

    def test_due_words(self):
        """Words with past next_review should be due."""
        now = datetime.now()
        # Past due
        db.upsert_word_review(
            word="due_word", mastery_level=MASTERY_LEARNING,
            consecutive_correct=0, review_interval_days=1,
            ease_factor=2.5, last_reviewed=now.isoformat(),
            next_review=(now - timedelta(days=1)).isoformat(),
            total_reviews=1, total_correct=0, total_incorrect=1,
        )
        # Future due
        db.upsert_word_review(
            word="future_word", mastery_level=MASTERY_FAMILIAR,
            consecutive_correct=2, review_interval_days=3,
            ease_factor=2.5, last_reviewed=now.isoformat(),
            next_review=(now + timedelta(days=3)).isoformat(),
            total_reviews=2, total_correct=2, total_incorrect=0,
        )
        due = db.get_words_due_for_review()
        due_words = [d["word"] for d in due]
        self.assertIn("due_word", due_words)
        self.assertNotIn("future_word", due_words)

    def test_mastery_distribution(self):
        """Test mastery distribution counts."""
        now = datetime.now()
        for word, mastery in [("w1", MASTERY_LEARNING), ("w2", MASTERY_LEARNING),
                               ("w3", MASTERY_FAMILIAR), ("w4", MASTERY_MASTERED)]:
            db.upsert_word_review(
                word=word, mastery_level=mastery, consecutive_correct=1,
                review_interval_days=1, ease_factor=2.5,
                last_reviewed=now.isoformat(),
                next_review=(now + timedelta(days=1)).isoformat(),
                total_reviews=1, total_correct=1, total_incorrect=0,
            )
        dist = db.get_mastery_distribution()
        self.assertEqual(dist["learning"], 2)
        self.assertEqual(dist["familiar"], 1)
        self.assertEqual(dist["mastered"], 1)

    def test_weak_words(self):
        """Test weak word identification by error rate."""
        now = datetime.now()
        db.upsert_word_review(
            word="weak_word", mastery_level=MASTERY_LEARNING,
            consecutive_correct=0, review_interval_days=1, ease_factor=2.5,
            last_reviewed=now.isoformat(),
            next_review=(now + timedelta(days=1)).isoformat(),
            total_reviews=5, total_correct=1, total_incorrect=4,
        )
        db.upsert_word_review(
            word="strong_word", mastery_level=MASTERY_MASTERED,
            consecutive_correct=5, review_interval_days=15, ease_factor=2.5,
            last_reviewed=now.isoformat(),
            next_review=(now + timedelta(days=15)).isoformat(),
            total_reviews=5, total_correct=5, total_incorrect=0,
        )
        weak = db.get_weak_words(limit=10)
        self.assertEqual(weak[0]["word"], "weak_word")

    def test_reviews_today(self):
        """Test counting reviews done today."""
        now = datetime.now()
        db.record_review_log(
            word="w1", was_correct=True, quality=5,
            review_time=now.isoformat(), interval_before=1, interval_after=3,
            mastery_before=MASTERY_LEARNING, mastery_after=MASTERY_FAMILIAR,
        )
        db.record_review_log(
            word="w2", was_correct=False, quality=2,
            review_time=now.isoformat(), interval_before=3, interval_after=1,
            mastery_before=MASTERY_FAMILIAR, mastery_after=MASTERY_LEARNING,
        )
        count = db.get_reviews_today()
        self.assertEqual(count, 2)

    def test_wrong_words_by_category(self):
        """Test filtering wrong words by error category."""
        db.record_wrong_word("w1", "w1x", "w1", "spelling")
        db.record_wrong_word("w2", "w2x", "w2", "confusable")
        db.record_wrong_word("w3", "w3x", "w3", "spelling")
        spelling_words = db.get_wrong_words_by_category("spelling")
        self.assertEqual(len(spelling_words), 2)
        confusable_words = db.get_wrong_words_by_category("confusable")
        self.assertEqual(len(confusable_words), 1)

    def test_remove_wrong_word_if_mastered(self):
        """A mastered word should be removed from the wrong-word notebook."""
        db.record_wrong_word("mastered_word", "mwordx", "mastered_word", "spelling")
        now = datetime.now()
        db.upsert_word_review(
            word="mastered_word", mastery_level=MASTERY_MASTERED,
            consecutive_correct=3, review_interval_days=7, ease_factor=2.5,
            last_reviewed=now.isoformat(),
            next_review=(now + timedelta(days=7)).isoformat(),
            total_reviews=5, total_correct=3, total_incorrect=2,
        )
        removed = db.remove_wrong_word_if_mastered("mastered_word")
        self.assertTrue(removed)
        wrong = db.get_wrong_words()
        self.assertEqual(len(wrong), 0)

    def test_do_not_remove_unmastered_wrong_word(self):
        """A non-mastered word should NOT be removed from the wrong-word notebook."""
        db.record_wrong_word("learning_word", "lwordx", "learning_word", "spelling")
        removed = db.remove_wrong_word_if_mastered("learning_word")
        self.assertFalse(removed)
        wrong = db.get_wrong_words()
        self.assertEqual(len(wrong), 1)

    def test_accuracy_trend(self):
        """Test the 7-day accuracy trend returns 7 entries."""
        trend = db.get_recent_accuracy_trend(days=7)
        self.assertEqual(len(trend), 7)
        for day in trend:
            self.assertIn("date", day)
            self.assertIn("total", day)
            self.assertIn("correct", day)
            self.assertIn("accuracy", day)

    def test_safe_migration_no_data_loss(self):
        """Re-running init_db should not destroy existing data."""
        db.record_wrong_word("safe_word", "swx", "safe_word", "spelling")
        db.upsert_word_review(
            word="safe_word", mastery_level=MASTERY_LEARNING,
            consecutive_correct=1, review_interval_days=1, ease_factor=2.5,
            last_reviewed=datetime.now().isoformat(),
            next_review=(datetime.now() + timedelta(days=1)).isoformat(),
            total_reviews=1, total_correct=0, total_incorrect=1,
        )
        # Re-init
        db.init_db()
        # Data should still be there
        self.assertIsNotNone(db.get_word_review("safe_word"))
        self.assertEqual(len(db.get_wrong_words()), 1)


class TestFullReviewCycle(unittest.TestCase):
    """
    Integration test: simulate a full review cycle through the database,
    verifying that spaced-repetition state is correctly persisted.
    """

    def setUp(self):
        db.init_db()
        db.reset_all_data()

    def tearDown(self):
        db.reset_all_data()

    def test_correct_answer_increases_interval_in_db(self):
        """A correct answer should increase the interval in the database."""
        word = "cycle_word"
        now = datetime.now()

        # First review: correct
        result = compute_next_review(True, 0, 0, DEFAULT_EASE_FACTOR)
        mastery = determine_mastery(
            result["new_consecutive_correct"], result["new_interval"],
            True, is_first_review=True
        )
        db.upsert_word_review(
            word=word, mastery_level=mastery,
            consecutive_correct=result["new_consecutive_correct"],
            review_interval_days=result["new_interval"],
            ease_factor=result["new_ease_factor"],
            last_reviewed=now.isoformat(),
            next_review=result["next_review_date"],
            total_reviews=1, total_correct=1, total_incorrect=0,
        )
        review = db.get_word_review(word)
        self.assertEqual(review["review_interval_days"], 1)
        self.assertEqual(review["consecutive_correct"], 1)

        # Second review: correct
        result2 = compute_next_review(True, 1, 1, result["new_ease_factor"])
        mastery2 = determine_mastery(
            result2["new_consecutive_correct"], result2["new_interval"],
            True, is_first_review=False
        )
        db.upsert_word_review(
            word=word, mastery_level=mastery2,
            consecutive_correct=result2["new_consecutive_correct"],
            review_interval_days=result2["new_interval"],
            ease_factor=result2["new_ease_factor"],
            last_reviewed=now.isoformat(),
            next_review=result2["next_review_date"],
            total_reviews=2, total_correct=2, total_incorrect=0,
        )
        review2 = db.get_word_review(word)
        self.assertEqual(review2["review_interval_days"], 3)
        self.assertEqual(review2["consecutive_correct"], 2)
        self.assertEqual(review2["mastery_level"], MASTERY_FAMILIAR)

    def test_incorrect_answer_resets_in_db(self):
        """An incorrect answer should reset the interval in the database."""
        word = "reset_word"
        now = datetime.now()

        # Build up to interval 3
        db.upsert_word_review(
            word=word, mastery_level=MASTERY_FAMILIAR,
            consecutive_correct=2, review_interval_days=3, ease_factor=2.5,
            last_reviewed=now.isoformat(),
            next_review=(now + timedelta(days=3)).isoformat(),
            total_reviews=2, total_correct=2, total_incorrect=0,
        )

        # Incorrect answer
        result = compute_next_review(False, 2, 3, 2.5)
        mastery = determine_mastery(
            result["new_consecutive_correct"], result["new_interval"],
            False, is_first_review=False
        )
        db.upsert_word_review(
            word=word, mastery_level=mastery,
            consecutive_correct=result["new_consecutive_correct"],
            review_interval_days=result["new_interval"],
            ease_factor=result["new_ease_factor"],
            last_reviewed=now.isoformat(),
            next_review=result["next_review_date"],
            total_reviews=3, total_correct=2, total_incorrect=1,
        )
        review = db.get_word_review(word)
        self.assertEqual(review["review_interval_days"], 1)
        self.assertEqual(review["consecutive_correct"], 0)
        self.assertEqual(review["mastery_level"], MASTERY_LEARNING)


if __name__ == "__main__":
    unittest.main()
