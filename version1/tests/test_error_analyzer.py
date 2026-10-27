"""
Tests for the error analyzer module.
Covers all three error categories plus edge cases:
  - Correct spelling (exact match)
  - Capitalization differences (should be treated as correct)
  - Common spelling mistakes (small edit distance)
  - Known confusing-word pairs (confusable detection)
  - Incorrect Chinese meaning selection (meaning error)
  - Unrelated incorrect answers (must NOT be classified as confusable)
  - Wrong-word recording in the database
"""

import sys
import os
import unittest

# Add the parent directory to sys.path so we can import the application modules.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from error_analyzer import (
    analyze_spelling_answer,
    analyze_meaning_answer,
    levenshtein_distance,
    get_category_label,
)
import database as db


class TestLevenshteinDistance(unittest.TestCase):
    """Tests for the Levenshtein edit-distance function."""

    def test_identical_strings(self):
        self.assertEqual(levenshtein_distance("hello", "hello"), 0)

    def test_one_substitution(self):
        self.assertEqual(levenshtein_distance("cat", "cot"), 1)

    def test_one_deletion(self):
        self.assertEqual(levenshtein_distance("cats", "cat"), 1)

    def test_one_insertion(self):
        self.assertEqual(levenshtein_distance("cat", "cats"), 1)

    def test_completely_different(self):
        self.assertEqual(levenshtein_distance("abc", "xyz"), 3)

    def test_empty_string(self):
        self.assertEqual(levenshtein_distance("", "abc"), 3)
        self.assertEqual(levenshtein_distance("abc", ""), 3)


class TestCorrectSpelling(unittest.TestCase):
    """Correct answers should be recognised as correct."""

    def test_exact_match(self):
        result = analyze_spelling_answer("accept", "accept")
        self.assertTrue(result["is_correct"])
        self.assertIsNone(result["error_category"])

    def test_match_with_spaces(self):
        result = analyze_spelling_answer("  accept  ", "accept")
        self.assertTrue(result["is_correct"])


class TestCapitalizationDifferences(unittest.TestCase):
    """Capitalization differences should be treated as correct (normalized comparison)."""

    def test_all_uppercase(self):
        result = analyze_spelling_answer("ACCEPT", "accept")
        self.assertTrue(result["is_correct"])

    def test_mixed_case(self):
        result = analyze_spelling_answer("AcCePt", "accept")
        self.assertTrue(result["is_correct"])

    def test_first_letter_capital(self):
        result = analyze_spelling_answer("Accept", "accept")
        self.assertTrue(result["is_correct"])


class TestSpellingErrors(unittest.TestCase):
    """Common spelling mistakes (small edit distance) should be classified as 'spelling'."""

    def test_single_letter_typo(self):
        # "accpet" → "accept": one transposition = edit distance 2
        result = analyze_spelling_answer("accpet", "accept")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "spelling")

    def test_missing_letter(self):
        # "accep" → "accept": one deletion = edit distance 1
        result = analyze_spelling_answer("accep", "accept")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "spelling")

    def test_extra_letter(self):
        # "acceptt" → "accept": one insertion = edit distance 1
        result = analyze_spelling_answer("acceptt", "accept")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "spelling")

    def test_wrong_letter(self):
        # "axcept" → "accept": one substitution = edit distance 1
        result = analyze_spelling_answer("axcept", "accept")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "spelling")


class TestConfusableWords(unittest.TestCase):
    """Known confusable-word pairs should be classified as 'confusable'."""

    def test_accept_vs_except(self):
        # Student types "except" when the answer is "accept"
        result = analyze_spelling_answer("except", "accept", confusable_group=["accept", "except"])
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "confusable")

    def test_except_vs_accept(self):
        # Student types "accept" when the answer is "except"
        result = analyze_spelling_answer("accept", "except", confusable_group=["accept", "except"])
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "confusable")

    def test_affect_vs_effect(self):
        result = analyze_spelling_answer("effect", "affect", confusable_group=["affect", "effect"])
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "confusable")

    def test_quite_vs_quiet(self):
        result = analyze_spelling_answer("quiet", "quite", confusable_group=["quite", "quiet"])
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "confusable")

    def test_their_vs_there(self):
        result = analyze_spelling_answer("there", "their", confusable_group=["their", "there"])
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "confusable")

    def test_confusable_with_capitalization(self):
        # Confusable detection should also work with different capitalization
        result = analyze_spelling_answer("Except", "accept", confusable_group=["accept", "except"])
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "confusable")


class TestUnrelatedAnswers(unittest.TestCase):
    """
    Unrelated incorrect answers (large edit distance, no confusable match)
    must NOT be classified as 'confusable'. They should be 'unrelated'.
    """

    def test_completely_different_word(self):
        # "apple" vs "accept" — unrelated, not a confusable partner
        result = analyze_spelling_answer("apple", "accept", confusable_group=["accept", "except"])
        self.assertFalse(result["is_correct"])
        self.assertNotEqual(result["error_category"], "confusable")
        self.assertEqual(result["error_category"], "unrelated")

    def test_random_word_no_confusable_group(self):
        # No confusable group provided; a very different word is 'unrelated'
        result = analyze_spelling_answer("xylophone", "abandon")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "unrelated")

    def test_short_unrelated_word(self):
        # "dog" vs "accept" — large edit distance, unrelated
        result = analyze_spelling_answer("dog", "accept")
        self.assertFalse(result["is_correct"])
        self.assertNotEqual(result["error_category"], "confusable")

    def test_empty_answer(self):
        result = analyze_spelling_answer("", "accept")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "unrelated")


class TestMeaningErrors(unittest.TestCase):
    """Incorrect Chinese meaning selection should be classified as 'meaning'."""

    def test_correct_meaning(self):
        result = analyze_meaning_answer("接受", "接受")
        self.assertTrue(result["is_correct"])
        self.assertIsNone(result["error_category"])

    def test_wrong_meaning(self):
        result = analyze_meaning_answer("除了", "接受")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "meaning")

    def test_wrong_meaning_with_spaces(self):
        result = analyze_meaning_answer("  除了  ", "接受")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "meaning")

    def test_empty_meaning_selection(self):
        result = analyze_meaning_answer("", "接受")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["error_category"], "meaning")


class TestCategoryLabels(unittest.TestCase):
    """Error category labels should return readable Chinese text."""

    def test_spelling_label(self):
        self.assertEqual(get_category_label("spelling"), "拼写错误")

    def test_confusable_label(self):
        self.assertEqual(get_category_label("confusable"), "形近词混淆")

    def test_meaning_label(self):
        self.assertEqual(get_category_label("meaning"), "词义答错")

    def test_unrelated_label(self):
        self.assertEqual(get_category_label("unrelated"), "答案不正确")


class TestWrongWordRecording(unittest.TestCase):
    """Test that wrong words are correctly recorded in the SQLite database."""

    def setUp(self):
        """Use a fresh in-memory-style database by resetting all data."""
        db.init_db()
        db.reset_all_data()

    def tearDown(self):
        db.reset_all_data()

    def test_record_and_retrieve(self):
        db.record_wrong_word("accept", "except", "accept", "confusable")
        words = db.get_wrong_words()
        self.assertEqual(len(words), 1)
        self.assertEqual(words[0]["word"], "accept")
        self.assertEqual(words[0]["student_answer"], "except")
        self.assertEqual(words[0]["error_category"], "confusable")
        self.assertEqual(words[0]["mistake_count"], 1)

    def test_increment_mistake_count(self):
        # Record the same word twice — mistake_count should become 2.
        db.record_wrong_word("abandon", "abandn", "abandon", "spelling")
        db.record_wrong_word("abandon", "abanddon", "abandon", "spelling")
        words = db.get_wrong_words()
        self.assertEqual(len(words), 1)
        self.assertEqual(words[0]["mistake_count"], 2)

    def test_delete_wrong_word(self):
        db.record_wrong_word("test_word", "tset", "test_word", "spelling")
        words = db.get_wrong_words()
        self.assertEqual(len(words), 1)
        word_id = words[0]["id"]
        deleted = db.delete_wrong_word(word_id)
        self.assertTrue(deleted)
        self.assertEqual(len(db.get_wrong_words()), 0)

    def test_practice_stats_update(self):
        db.update_practice_stats(10, 7, 3)
        stats = db.get_practice_stats()
        self.assertEqual(stats["total_questions"], 10)
        self.assertEqual(stats["correct_answers"], 7)
        self.assertEqual(stats["incorrect_answers"], 3)

    def test_wrong_word_count(self):
        db.record_wrong_word("word1", "wrod1", "word1", "spelling")
        db.record_wrong_word("word2", "word3", "word2", "unrelated")
        self.assertEqual(db.get_wrong_word_count(), 2)


if __name__ == "__main__":
    unittest.main()
