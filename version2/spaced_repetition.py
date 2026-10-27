"""
Spaced-repetition scheduling algorithm (SM-2-inspired) for Version 2.

This is a SIMPLIFIED adaptation of the SM-2 algorithm (SuperMemo 2).
It is NOT a complete SM-2 implementation — it uses a simplified quality
grading (correct → q=5, incorrect → q=2) and a simplified interval schedule.

Core concepts preserved from SM-2:
  - Each item has an Ease Factor (EF), starting at 2.5, minimum 1.3.
  - A correct answer (q >= 3) increases the interval; an incorrect answer (q < 3)
    resets the repetition count and sets the interval to 1 day.
  - The EF is adjusted after each review based on response quality.
  - The interval grows multiplicatively using the EF.

Mastery levels (determined from consecutive correct answers and interval):
  - unlearned  (未学习):   never reviewed
  - learning   (学习中):   consecutive_correct < 2
  - familiar   (基本掌握):  consecutive_correct >= 2, but not yet mastered
  - mastered   (已掌握):    consecutive_correct >= 3 AND interval >= 7 days
"""

from datetime import datetime, timedelta

# --- Algorithm constants ---
DEFAULT_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3

# Quality grades (simplified from SM-2's 0-5 scale).
QUALITY_CORRECT = 5      # Perfect or near-perfect recall
QUALITY_INCORRECT = 2    # Failed recall

# --- Mastery level constants ---
MASTERY_UNLEARNED = "unlearned"
MASTERY_LEARNING = "learning"
MASTERY_FAMILIAR = "familiar"
MASTERY_MASTERED = "mastered"

# Human-readable Chinese labels for mastery levels.
MASTERY_LABELS = {
    MASTERY_UNLEARNED: "未学习",
    MASTERY_LEARNING: "学习中",
    MASTERY_FAMILIAR: "基本掌握",
    MASTERY_MASTERED: "已掌握",
}

# Mastery threshold: consecutive correct answers needed for "mastered".
MASTERY_CORRECT_THRESHOLD = 3
# Interval threshold (days) needed for "mastered".
MASTERY_INTERVAL_THRESHOLD = 7


def compute_next_review(was_correct, consecutive_correct, current_interval, ease_factor):
    """
    Compute the next review state after a practice attempt.

    This is the core SM-2-inspired scheduling function.

    Args:
        was_correct:          Whether the student answered correctly (bool).
        consecutive_correct:  Current streak of correct answers before this review.
        current_interval:     Current review interval in days (before this review).
        ease_factor:          Current ease factor (before this review).

    Returns:
        A dict with:
            new_interval:            New review interval in days.
            new_ease_factor:         Updated ease factor (>= MIN_EASE_FACTOR).
            new_consecutive_correct: Updated consecutive correct count.
            quality:                 The quality grade used (0-5).
            next_review_date:       ISO datetime string for the next scheduled review.
    """
    # Determine quality grade.
    if was_correct:
        quality = QUALITY_CORRECT
        new_consecutive = consecutive_correct + 1
    else:
        quality = QUALITY_INCORRECT
        new_consecutive = 0

    # Compute new interval following SM-2-inspired rules.
    if quality < 3:
        # Failed recall: reset to 1 day.
        new_interval = 1
    else:
        if new_consecutive == 1:
            new_interval = 1
        elif new_consecutive == 2:
            new_interval = 3
        else:
            # Interval grows by multiplying with the ease factor.
            new_interval = max(1, round(current_interval * ease_factor))

    # Update ease factor using the SM-2 formula.
    new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ease < MIN_EASE_FACTOR:
        new_ease = MIN_EASE_FACTOR

    # Round ease factor to 2 decimal places for clean storage.
    new_ease = round(new_ease, 2)

    # Compute the next review datetime.
    now = datetime.now()
    next_review = now + timedelta(days=new_interval)

    return {
        "new_interval": new_interval,
        "new_ease_factor": new_ease,
        "new_consecutive_correct": new_consecutive,
        "quality": quality,
        "next_review_date": next_review.isoformat(),
    }


def determine_mastery(consecutive_correct, interval, was_correct, is_first_review=False):
    """
    Determine the mastery level based on review history.

    Args:
        consecutive_correct:  Current streak of correct answers (after this review).
        interval:             Current review interval in days (after this review).
        was_correct:          Whether the most recent answer was correct.
        is_first_review:      Whether this is the word's first ever review.

    Returns:
        One of the MASTERY_* constants.
    """
    if is_first_review:
        # First review always puts the word in "learning" (regardless of correctness).
        return MASTERY_LEARNING

    if not was_correct:
        # Incorrect answer drops back to "learning".
        return MASTERY_LEARNING

    # Check for mastered: enough consecutive correct AND long enough interval.
    if consecutive_correct >= MASTERY_CORRECT_THRESHOLD and interval >= MASTERY_INTERVAL_THRESHOLD:
        return MASTERY_MASTERED

    # Check for familiar: at least 2 consecutive correct.
    if consecutive_correct >= 2:
        return MASTERY_FAMILIAR

    # Otherwise still learning.
    return MASTERY_LEARNING


def get_mastery_label(mastery_level):
    """Return the Chinese label for a mastery level."""
    return MASTERY_LABELS.get(mastery_level, mastery_level or "未知")


def is_due_for_review(next_review_str, now=None):
    """
    Check whether a word is due for review.

    Args:
        next_review_str: ISO datetime string for the next scheduled review.
        now:             Optional datetime to compare against (defaults to now).

    Returns:
        True if the word's next review time has passed.
    """
    if not next_review_str:
        return True  # Never reviewed → due immediately.
    if now is None:
        now = datetime.now()
    try:
        next_review = datetime.fromisoformat(next_review_str)
        return now >= next_review
    except (ValueError, TypeError):
        return True  # Invalid date → treat as due.


def get_initial_review_state():
    """
    Return the initial review state for a brand-new word that has never been
    reviewed. The word starts as 'unlearned' with default ease factor and
    is immediately due for review.
    """
    now = datetime.now()
    return {
        "mastery_level": MASTERY_UNLEARNED,
        "consecutive_correct": 0,
        "review_interval_days": 0,
        "ease_factor": DEFAULT_EASE_FACTOR,
        "last_reviewed": None,
        "next_review": now.isoformat(),  # Due immediately.
        "total_reviews": 0,
        "total_correct": 0,
        "total_incorrect": 0,
    }
