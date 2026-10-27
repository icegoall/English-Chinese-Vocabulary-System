"""
Tests for the SM-2-inspired spaced-repetition algorithm.
Covers:
  - First-time review scheduling
  - Correct-answer interval increases
  - Incorrect-answer interval resets
  - Ease factor updates
  - Due-date calculation
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from spaced_repetition import (
    compute_next_review,
    determine_mastery,
    is_due_for_review,
    get_initial_review_state,
    get_mastery_label,
    DEFAULT_EASE_FACTOR,
    MIN_EASE_FACTOR,
    MASTERY_UNLEARNED,
    MASTERY_LEARNING,
    MASTERY_FAMILIAR,
    MASTERY_MASTERED,
    QUALITY_CORRECT,
    QUALITY_INCORRECT,
)


class TestComputeNextReview(unittest.TestCase):
    """Tests for the core spaced-repetition scheduling function."""

    def test_first_correct_answer(self):
        """First correct answer: interval = 1, consecutive = 1."""
        result = compute_next_review(
            was_correct=True, consecutive_correct=0,
            current_interval=0, ease_factor=DEFAULT_EASE_FACTOR
        )
        self.assertEqual(result["new_interval"], 1)
        self.assertEqual(result["new_consecutive_correct"], 1)
        self.assertEqual(result["quality"], QUALITY_CORRECT)

    def test_second_correct_answer(self):
        """Second correct answer: interval = 3, consecutive = 2."""
        result = compute_next_review(
            was_correct=True, consecutive_correct=1,
            current_interval=1, ease_factor=DEFAULT_EASE_FACTOR
        )
        self.assertEqual(result["new_interval"], 3)
        self.assertEqual(result["new_consecutive_correct"], 2)

    def test_third_correct_answer_interval_grows(self):
        """Third correct answer: interval grows by multiplying with ease factor."""
        result = compute_next_review(
            was_correct=True, consecutive_correct=2,
            current_interval=3, ease_factor=DEFAULT_EASE_FACTOR
        )
        # round(3 * 2.5) = round(7.5) = 8
        self.assertEqual(result["new_interval"], 8)
        self.assertEqual(result["new_consecutive_correct"], 3)

    def test_interval_increases_with_consecutive_correct(self):
        """Each correct answer should increase (or maintain) the interval."""
        interval = 0
        consecutive = 0
        ef = DEFAULT_EASE_FACTOR
        intervals = []
        for _ in range(5):
            result = compute_next_review(True, consecutive, interval, ef)
            intervals.append(result["new_interval"])
            consecutive = result["new_consecutive_correct"]
            interval = result["new_interval"]
            ef = result["new_ease_factor"]
        # Intervals should be non-decreasing: [1, 3, 8, ...]
        for i in range(1, len(intervals)):
            self.assertGreaterEqual(intervals[i], intervals[i - 1])

    def test_incorrect_answer_resets_interval(self):
        """Incorrect answer resets interval to 1 and consecutive to 0."""
        result = compute_next_review(
            was_correct=False, consecutive_correct=5,
            current_interval=30, ease_factor=DEFAULT_EASE_FACTOR
        )
        self.assertEqual(result["new_interval"], 1)
        self.assertEqual(result["new_consecutive_correct"], 0)
        self.assertEqual(result["quality"], QUALITY_INCORRECT)

    def test_incorrect_after_correct_resets(self):
        """Incorrect answer after a streak resets consecutive to 0."""
        result = compute_next_review(
            was_correct=False, consecutive_correct=3,
            current_interval=8, ease_factor=DEFAULT_EASE_FACTOR
        )
        self.assertEqual(result["new_consecutive_correct"], 0)
        self.assertEqual(result["new_interval"], 1)

    def test_ease_factor_does_not_go_below_minimum(self):
        """Ease factor should never drop below MIN_EASE_FACTOR (1.3)."""
        ef = DEFAULT_EASE_FACTOR
        for _ in range(20):
            result = compute_next_review(False, 0, 1, ef)
            ef = result["new_ease_factor"]
        self.assertGreaterEqual(ef, MIN_EASE_FACTOR)

    def test_ease_factor_decreases_on_incorrect(self):
        """Incorrect answers should decrease the ease factor."""
        result = compute_next_review(
            was_correct=False, consecutive_correct=0,
            current_interval=1, ease_factor=DEFAULT_EASE_FACTOR
        )
        self.assertLess(result["new_ease_factor"], DEFAULT_EASE_FACTOR)

    def test_ease_factor_increases_on_perfect_correct(self):
        """A perfect correct answer (q=5) increases the ease factor by 0.1 (SM-2 formula)."""
        result = compute_next_review(
            was_correct=True, consecutive_correct=0,
            current_interval=0, ease_factor=DEFAULT_EASE_FACTOR
        )
        # SM-2: EF' = EF + (0.1 - (5-5)*(0.08 + (5-5)*0.02)) = EF + 0.1
        self.assertAlmostEqual(result["new_ease_factor"], DEFAULT_EASE_FACTOR + 0.1, places=2)

    def test_next_review_date_in_future(self):
        """Next review date should be in the future for a correct answer."""
        result = compute_next_review(
            was_correct=True, consecutive_correct=2,
            current_interval=3, ease_factor=DEFAULT_EASE_FACTOR
        )
        next_review = datetime.fromisoformat(result["next_review_date"])
        now = datetime.now()
        self.assertGreater(next_review, now)

    def test_next_review_date_one_day_for_incorrect(self):
        """Incorrect answer schedules review 1 day later."""
        result = compute_next_review(
            was_correct=False, consecutive_correct=3,
            current_interval=10, ease_factor=DEFAULT_EASE_FACTOR
        )
        next_review = datetime.fromisoformat(result["next_review_date"])
        now = datetime.now()
        diff = next_review - now
        # Should be approximately 1 day (allow small tolerance for execution time)
        self.assertGreater(diff.total_seconds(), 86000)
        self.assertLess(diff.total_seconds(), 90000)


class TestDetermineMastery(unittest.TestCase):
    """Tests for mastery level determination."""

    def test_first_review_always_learning(self):
        """First review should always result in 'learning'."""
        m = determine_mastery(1, 1, True, is_first_review=True)
        self.assertEqual(m, MASTERY_LEARNING)
        m = determine_mastery(0, 1, False, is_first_review=True)
        self.assertEqual(m, MASTERY_LEARNING)

    def test_incorrect_drops_to_learning(self):
        """Incorrect answer always drops to 'learning'."""
        m = determine_mastery(0, 1, False, is_first_review=False)
        self.assertEqual(m, MASTERY_LEARNING)

    def test_one_correct_is_learning(self):
        """One consecutive correct (not first review) is still 'learning'."""
        m = determine_mastery(1, 1, True, is_first_review=False)
        self.assertEqual(m, MASTERY_LEARNING)

    def test_two_correct_is_familiar(self):
        """Two consecutive correct is 'familiar'."""
        m = determine_mastery(2, 3, True, is_first_review=False)
        self.assertEqual(m, MASTERY_FAMILIAR)

    def test_three_correct_short_interval_is_familiar(self):
        """Three correct but short interval (< 7) is 'familiar', not 'mastered'."""
        m = determine_mastery(3, 3, True, is_first_review=False)
        self.assertEqual(m, MASTERY_FAMILIAR)

    def test_three_correct_long_interval_is_mastered(self):
        """Three correct AND interval >= 7 is 'mastered'."""
        m = determine_mastery(3, 7, True, is_first_review=False)
        self.assertEqual(m, MASTERY_MASTERED)

    def test_many_correct_long_interval_is_mastered(self):
        """Many correct with long interval is 'mastered'."""
        m = determine_mastery(10, 30, True, is_first_review=False)
        self.assertEqual(m, MASTERY_MASTERED)

    def test_mastery_label(self):
        """Mastery labels should return Chinese text."""
        self.assertEqual(get_mastery_label(MASTERY_UNLEARNED), "未学习")
        self.assertEqual(get_mastery_label(MASTERY_LEARNING), "学习中")
        self.assertEqual(get_mastery_label(MASTERY_FAMILIAR), "基本掌握")
        self.assertEqual(get_mastery_label(MASTERY_MASTERED), "已掌握")


class TestIsDueForReview(unittest.TestCase):
    """Tests for due-date checking."""

    def test_none_next_review_is_due(self):
        """No next_review date means the word is due."""
        self.assertTrue(is_due_for_review(None))

    def test_past_date_is_due(self):
        """A past next_review date means the word is due."""
        past = (datetime.now() - timedelta(days=1)).isoformat()
        self.assertTrue(is_due_for_review(past))

    def test_future_date_not_due(self):
        """A future next_review date means the word is not due."""
        future = (datetime.now() + timedelta(days=5)).isoformat()
        self.assertFalse(is_due_for_review(future))

    def test_empty_string_is_due(self):
        """Empty string next_review means due."""
        self.assertTrue(is_due_for_review(""))

    def test_invalid_date_is_due(self):
        """Invalid date string is treated as due."""
        self.assertTrue(is_due_for_review("not-a-date"))


class TestInitialReviewState(unittest.TestCase):
    """Tests for the initial review state of a new word."""

    def test_initial_state(self):
        state = get_initial_review_state()
        self.assertEqual(state["mastery_level"], MASTERY_UNLEARNED)
        self.assertEqual(state["consecutive_correct"], 0)
        self.assertEqual(state["review_interval_days"], 0)
        self.assertEqual(state["ease_factor"], DEFAULT_EASE_FACTOR)
        self.assertIsNone(state["last_reviewed"])
        self.assertEqual(state["total_reviews"], 0)
        self.assertEqual(state["total_correct"], 0)
        self.assertEqual(state["total_incorrect"], 0)

    def test_initial_state_is_due_immediately(self):
        """Initial next_review should be now (due immediately)."""
        state = get_initial_review_state()
        self.assertTrue(is_due_for_review(state["next_review"]))


if __name__ == "__main__":
    unittest.main()
