"""
Tests for mastery-level transitions and the full practice-to-mastery pipeline.
Covers:
  - Mastery transitions: unlearned → learning → familiar → mastered
  - Mastery regression on incorrect answers
  - Targeted wrong-word practice question generation
  - Dashboard statistics accuracy
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import database as db
import vocabulary as vocab
from spaced_repetition import (
    compute_next_review,
    determine_mastery,
    get_mastery_label,
    DEFAULT_EASE_FACTOR,
    MASTERY_UNLEARNED,
    MASTERY_LEARNING,
    MASTERY_FAMILIAR,
    MASTERY_MASTERED,
)


class TestMasteryTransitions(unittest.TestCase):
    """Test mastery level transitions through the learning lifecycle."""

    def setUp(self):
        db.init_db()
        db.reset_all_data()

    def tearDown(self):
        db.reset_all_data()

    def test_unlearned_to_learning(self):
        """First review transitions from unlearned to learning."""
        # First correct answer
        result = compute_next_review(True, 0, 0, DEFAULT_EASE_FACTOR)
        mastery = determine_mastery(
            result["new_consecutive_correct"], result["new_interval"],
            True, is_first_review=True
        )
        self.assertEqual(mastery, MASTERY_LEARNING)

    def test_learning_to_familiar(self):
        """Two consecutive correct answers transition to familiar."""
        # After 2nd correct: consecutive=2, interval=3
        mastery = determine_mastery(2, 3, True, is_first_review=False)
        self.assertEqual(mastery, MASTERY_FAMILIAR)

    def test_familiar_to_mastered(self):
        """Three consecutive correct with interval >= 7 transitions to mastered."""
        # After 3rd correct: consecutive=3, interval=8 (round(3*2.5))
        mastery = determine_mastery(3, 8, True, is_first_review=False)
        self.assertEqual(mastery, MASTERY_MASTERED)

    def test_mastered_stays_mastered_on_correct(self):
        """A mastered word stays mastered on another correct answer."""
        mastery = determine_mastery(5, 20, True, is_first_review=False)
        self.assertEqual(mastery, MASTERY_MASTERED)

    def test_mastered_drops_to_learning_on_incorrect(self):
        """An incorrect answer drops mastery from mastered to learning."""
        mastery = determine_mastery(0, 1, False, is_first_review=False)
        self.assertEqual(mastery, MASTERY_LEARNING)

    def test_familiar_drops_to_learning_on_incorrect(self):
        """An incorrect answer drops mastery from familiar to learning."""
        mastery = determine_mastery(0, 1, False, is_first_review=False)
        self.assertEqual(mastery, MASTERY_LEARNING)

    def test_full_lifecycle_in_db(self):
        """Simulate a full lifecycle: unlearned → learning → familiar → mastered → (incorrect) → learning."""
        word = "lifecycle_word"
        now = datetime.now()

        # Step 1: First correct → learning
        r1 = compute_next_review(True, 0, 0, DEFAULT_EASE_FACTOR)
        m1 = determine_mastery(r1["new_consecutive_correct"], r1["new_interval"], True, True)
        db.upsert_word_review(word, m1, r1["new_consecutive_correct"], r1["new_interval"],
                              r1["new_ease_factor"], now.isoformat(), r1["next_review_date"], 1, 1, 0)
        self.assertEqual(db.get_word_review(word)["mastery_level"], MASTERY_LEARNING)

        # Step 2: Second correct → familiar
        r2 = compute_next_review(True, 1, r1["new_interval"], r1["new_ease_factor"])
        m2 = determine_mastery(r2["new_consecutive_correct"], r2["new_interval"], True, False)
        db.upsert_word_review(word, m2, r2["new_consecutive_correct"], r2["new_interval"],
                              r2["new_ease_factor"], now.isoformat(), r2["next_review_date"], 2, 2, 0)
        self.assertEqual(db.get_word_review(word)["mastery_level"], MASTERY_FAMILIAR)

        # Step 3: Third correct → mastered (interval should be >= 7)
        r3 = compute_next_review(True, 2, r2["new_interval"], r2["new_ease_factor"])
        m3 = determine_mastery(r3["new_consecutive_correct"], r3["new_interval"], True, False)
        db.upsert_word_review(word, m3, r3["new_consecutive_correct"], r3["new_interval"],
                              r3["new_ease_factor"], now.isoformat(), r3["next_review_date"], 3, 3, 0)
        self.assertEqual(db.get_word_review(word)["mastery_level"], MASTERY_MASTERED)

        # Step 4: Incorrect → back to learning
        r4 = compute_next_review(False, 3, r3["new_interval"], r3["new_ease_factor"])
        m4 = determine_mastery(r4["new_consecutive_correct"], r4["new_interval"], False, False)
        db.upsert_word_review(word, m4, r4["new_consecutive_correct"], r4["new_interval"],
                              r4["new_ease_factor"], now.isoformat(), r4["next_review_date"], 4, 3, 1)
        self.assertEqual(db.get_word_review(word)["mastery_level"], MASTERY_LEARNING)


class TestTargetedWrongWordPractice(unittest.TestCase):
    """Test targeted wrong-word practice question generation."""

    def setUp(self):
        db.init_db()
        db.reset_all_data()

    def tearDown(self):
        db.reset_all_data()

    def test_wrong_words_exist_for_practice(self):
        """After recording wrong words, they should be available for targeted practice."""
        db.record_wrong_word("accept", "except", "accept", "confusable")
        db.record_wrong_word("eager", "egar", "eager", "spelling")
        wrong = db.get_wrong_words()
        self.assertEqual(len(wrong), 2)

    def test_filter_by_category(self):
        """Wrong words can be filtered by error category for targeted practice."""
        db.record_wrong_word("w1", "w1x", "w1", "spelling")
        db.record_wrong_word("w2", "w2x", "w2", "confusable")
        db.record_wrong_word("w3", "w3x", "w3", "spelling")
        spelling_only = db.get_wrong_words_by_category("spelling")
        self.assertEqual(len(spelling_only), 2)
        for w in spelling_only:
            self.assertEqual(w["error_category"], "spelling")

    def test_vocabulary_lookup_for_wrong_words(self):
        """Wrong words should be found in the vocabulary library for question generation."""
        db.record_wrong_word("accept", "except", "accept", "confusable")
        wrong = db.get_wrong_words()
        for ww in wrong:
            entry = vocab.get_word_by_word(ww["word"])
            self.assertIsNotNone(entry)
            self.assertEqual(entry["word"], "accept")

    def test_mastered_word_removed_from_wrong_words(self):
        """When a word reaches mastered, it should be auto-removed from wrong words."""
        db.record_wrong_word("abandon", "abandn", "abandon", "spelling")
        now = datetime.now()
        db.upsert_word_review(
            word="abandon", mastery_level=MASTERY_MASTERED,
            consecutive_correct=3, review_interval_days=7, ease_factor=2.5,
            last_reviewed=now.isoformat(),
            next_review=(now + timedelta(days=7)).isoformat(),
            total_reviews=5, total_correct=3, total_incorrect=2,
        )
        removed = db.remove_wrong_word_if_mastered("abandon")
        self.assertTrue(removed)
        self.assertEqual(len(db.get_wrong_words()), 0)


class TestDashboardStatistics(unittest.TestCase):
    """Test that dashboard statistics are computed from real data."""

    def setUp(self):
        db.init_db()
        db.reset_all_data()

    def tearDown(self):
        db.reset_all_data()

    def test_mastery_distribution_counts(self):
        """Mastery distribution should reflect actual database records."""
        now = datetime.now()
        for word in ["w1", "w2", "w3"]:
            db.upsert_word_review(
                word=word, mastery_level=MASTERY_LEARNING,
                consecutive_correct=1, review_interval_days=1, ease_factor=2.5,
                last_reviewed=now.isoformat(),
                next_review=(now + timedelta(days=1)).isoformat(),
                total_reviews=1, total_correct=1, total_incorrect=0,
            )
        dist = db.get_mastery_distribution()
        self.assertEqual(dist["learning"], 3)
        self.assertEqual(dist["mastered"], 0)

    def test_due_count_reflects_database(self):
        """Due count should match the number of due words in the database."""
        now = datetime.now()
        # Two due, one not due
        db.upsert_word_review(
            word="due1", mastery_level=MASTERY_LEARNING,
            consecutive_correct=0, review_interval_days=1, ease_factor=2.5,
            last_reviewed=now.isoformat(),
            next_review=(now - timedelta(hours=1)).isoformat(),
            total_reviews=1, total_correct=0, total_incorrect=1,
        )
        db.upsert_word_review(
            word="due2", mastery_level=MASTERY_LEARNING,
            consecutive_correct=0, review_interval_days=1, ease_factor=2.5,
            last_reviewed=now.isoformat(),
            next_review=(now - timedelta(hours=2)).isoformat(),
            total_reviews=1, total_correct=0, total_incorrect=1,
        )
        db.upsert_word_review(
            word="not_due", mastery_level=MASTERY_FAMILIAR,
            consecutive_correct=2, review_interval_days=3, ease_factor=2.5,
            last_reviewed=now.isoformat(),
            next_review=(now + timedelta(days=3)).isoformat(),
            total_reviews=2, total_correct=2, total_incorrect=0,
        )
        due = db.get_words_due_for_review()
        self.assertEqual(len(due), 2)

    def test_reviews_today_count(self):
        """Reviews today count should match actual review logs."""
        now = datetime.now()
        for i in range(3):
            db.record_review_log(
                word=f"rw{i}", was_correct=True, quality=5,
                review_time=now.isoformat(), interval_before=1, interval_after=3,
                mastery_before=MASTERY_LEARNING, mastery_after=MASTERY_FAMILIAR,
            )
        self.assertEqual(db.get_reviews_today(), 3)

    def test_no_fake_statistics(self):
        """With no data, statistics should be zero, not fake."""
        dist = db.get_mastery_distribution()
        self.assertEqual(dist["unlearned"], 0)
        self.assertEqual(dist["learning"], 0)
        self.assertEqual(dist["familiar"], 0)
        self.assertEqual(dist["mastered"], 0)
        self.assertEqual(db.get_reviews_today(), 0)
        self.assertEqual(len(db.get_words_due_for_review()), 0)
        self.assertEqual(db.get_wrong_word_count(), 0)


if __name__ == "__main__":
    unittest.main()
