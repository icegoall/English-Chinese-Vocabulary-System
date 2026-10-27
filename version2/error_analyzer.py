"""
Intelligent error analyzer for the vocabulary system.

Identifies three categories of errors:
  1. spelling   — 拼写错误: the answer is close to the correct word (small edit distance)
                  but not exact, indicating a typo or spelling mistake.
  2. confusable — 形近词混淆: the answer matches a known confusable partner word
                  (e.g., "except" instead of "accept").
  3. meaning    — 词义答错: in English-to-Chinese mode, the student selected the
                  wrong Chinese meaning for a correctly displayed English word.

The analyzer also recognises "unrelated" answers (large edit distance, no confusable
match) which are recorded as wrong but NOT misclassified as confusable mistakes.
"""


def levenshtein_distance(s1, s2):
    """
    Compute the Levenshtein edit distance between two strings.
    This measures the minimum number of single-character edits (insertions,
    deletions, or substitutions) needed to change one string into the other.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def normalize(text):
    """Normalize a string for comparison: strip whitespace and convert to lowercase."""
    if text is None:
        return ""
    return text.strip().lower()


def analyze_spelling_answer(student_answer, correct_word, confusable_group=None):
    """
    Analyze a spelling-mode answer (Chinese-to-English: student types the English word).

    Args:
        student_answer:  The text the student typed.
        correct_word:    The correct English word.
        confusable_group: List of all words in the confusable group (including the
                         correct word), or None / empty list if no confusable partners.

    Returns:
        A dict with keys:
            is_correct:      True if the answer is correct.
            error_category:  One of None, 'spelling', 'confusable', 'unrelated'.
            explanation:     A Chinese explanation string for the student.
            edit_distance:   The Levenshtein distance between the answer and correct word.
    """
    norm_answer = normalize(student_answer)
    norm_correct = normalize(correct_word)

    # --- Check exact match (handles capitalization differences via normalization) ---
    if norm_answer == norm_correct:
        return {
            "is_correct": True,
            "error_category": None,
            "explanation": "回答正确！",
            "edit_distance": 0,
        }

    # --- Handle empty answer ---
    if norm_answer == "":
        return {
            "is_correct": False,
            "error_category": "unrelated",
            "explanation": f"未作答。正确答案是 '{correct_word}'。",
            "edit_distance": len(norm_correct),
        }

    # --- Check confusable-word confusion ---
    # Only classify as confusable if the student's answer exactly matches
    # a known confusable partner word (not the correct word itself).
    if confusable_group:
        for word in confusable_group:
            if normalize(word) == norm_answer and normalize(word) != norm_correct:
                return {
                    "is_correct": False,
                    "error_category": "confusable",
                    "explanation": (
                        f"形近词混淆：你输入的是 '{student_answer}'，"
                        f"它与 '{correct_word}' 是形近词，容易混淆。"
                        f"正确答案是 '{correct_word}'。"
                    ),
                    "edit_distance": levenshtein_distance(norm_answer, norm_correct),
                }

    # --- Check spelling error via edit distance ---
    distance = levenshtein_distance(norm_answer, norm_correct)
    # A small edit distance (1 or 2) suggests a typo / spelling mistake.
    # A large edit distance suggests the answer is unrelated (not a spelling slip).
    if distance <= 2:
        return {
            "is_correct": False,
            "error_category": "spelling",
            "explanation": (
                f"拼写错误：你输入的是 '{student_answer}'，"
                f"正确答案是 '{correct_word}'。请注意拼写。"
            ),
            "edit_distance": distance,
        }

    # --- Unrelated answer: wrong but not a spelling slip or confusable confusion ---
    return {
        "is_correct": False,
        "error_category": "unrelated",
        "explanation": (
            f"回答不正确：你输入的是 '{student_answer}'，"
            f"正确答案是 '{correct_word}'。请再复习一下这个单词。"
        ),
        "edit_distance": distance,
    }


def analyze_meaning_answer(selected_meaning, correct_meaning):
    """
    Analyze a meaning-mode answer (English-to-Chinese: student selects a Chinese meaning).

    Args:
        selected_meaning: The Chinese meaning the student selected.
        correct_meaning:  The correct Chinese meaning.

    Returns:
        A dict with keys:
            is_correct:      True if the selected meaning matches the correct one.
            error_category:  None if correct, 'meaning' if wrong.
            explanation:     A Chinese explanation string for the student.
    """
    norm_selected = normalize(selected_meaning)
    norm_correct = normalize(correct_meaning)

    if norm_selected == norm_correct:
        return {
            "is_correct": True,
            "error_category": None,
            "explanation": "回答正确！",
        }

    return {
        "is_correct": False,
        "error_category": "meaning",
        "explanation": (
            f"词义答错：你选择了 '{selected_meaning}'，"
            f"正确答案是 '{correct_meaning}'。请再看看这个单词的释义。"
        ),
    }


# Human-readable Chinese labels for each error category, used in the UI.
ERROR_CATEGORY_LABELS = {
    "spelling": "拼写错误",
    "confusable": "形近词混淆",
    "meaning": "词义答错",
    "unrelated": "答案不正确",
}


def get_category_label(category):
    """Return the Chinese label for an error category, or the raw category if unknown."""
    return ERROR_CATEGORY_LABELS.get(category, category or "未知")
