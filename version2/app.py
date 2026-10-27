"""
Flask application for Version 2 of the
中学生英语单词智能记忆与错词分析系统.

Version 2 adds:
  - SM-2-inspired spaced repetition scheduling
  - Vocabulary mastery tracking (unlearned → learning → familiar → mastered)
  - Targeted wrong-word practice (by category or specific word)
  - Daily review page for due words
  - Learning analytics dashboard

All Version 1 functionality is preserved.

Run with:
    python app.py
Then open http://127.0.0.1:5000 in a browser.
"""

import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

import database as db
import vocabulary as vocab
from error_analyzer import (
    analyze_spelling_answer,
    analyze_meaning_answer,
    get_category_label,
)
from spaced_repetition import (
    compute_next_review,
    determine_mastery,
    get_mastery_label,
    is_due_for_review,
    get_initial_review_state,
    MASTERY_UNLEARNED,
    MASTERY_LEARNING,
    MASTERY_FAMILIAR,
    MASTERY_MASTERED,
    DEFAULT_EASE_FACTOR,
)

app = Flask(__name__)
app.secret_key = "vocabulary-learning-system-v2-secret-key"

DEFAULT_QUESTION_COUNT = 10
CHOICE_COUNT = 4


# ===========================================================================
# Helper: update spaced-repetition state after a practice answer
# ===========================================================================

def update_word_review_state(word, was_correct, error_category=None):
    """
    Update the spaced-repetition state for a word after a practice attempt.
    Also logs the review event and removes the word from the wrong-word
    notebook if it reaches 'mastered' level.

    Args:
        word:           The vocabulary word being reviewed.
        was_correct:    Whether the student answered correctly.
        error_category: The error category (if incorrect), for logging.
    """
    existing = db.get_word_review(word)
    is_first = existing is None

    if is_first:
        consecutive_correct = 0
        current_interval = 0
        ease_factor = DEFAULT_EASE_FACTOR
        mastery_before = MASTERY_UNLEARNED
        total_reviews = 0
        total_correct = 0
        total_incorrect = 0
    else:
        consecutive_correct = existing["consecutive_correct"]
        current_interval = existing["review_interval_days"]
        ease_factor = existing["ease_factor"]
        mastery_before = existing["mastery_level"]
        total_reviews = existing["total_reviews"]
        total_correct = existing["total_correct"]
        total_incorrect = existing["total_incorrect"]

    interval_before = current_interval

    # Compute the new review state.
    result = compute_next_review(
        was_correct=was_correct,
        consecutive_correct=consecutive_correct,
        current_interval=current_interval,
        ease_factor=ease_factor,
    )

    new_interval = result["new_interval"]
    new_ease = result["new_ease_factor"]
    new_consecutive = result["new_consecutive_correct"]
    quality = result["quality"]
    next_review = result["next_review_date"]
    now_str = datetime.now().isoformat()

    # Determine the new mastery level.
    new_mastery = determine_mastery(
        consecutive_correct=new_consecutive,
        interval=new_interval,
        was_correct=was_correct,
        is_first_review=is_first,
    )

    # Update totals.
    new_total_reviews = total_reviews + 1
    new_total_correct = total_correct + (1 if was_correct else 0)
    new_total_incorrect = total_incorrect + (0 if was_correct else 1)

    # Persist the updated review state.
    db.upsert_word_review(
        word=word,
        mastery_level=new_mastery,
        consecutive_correct=new_consecutive,
        review_interval_days=new_interval,
        ease_factor=new_ease,
        last_reviewed=now_str,
        next_review=next_review,
        total_reviews=new_total_reviews,
        total_correct=new_total_correct,
        total_incorrect=new_total_incorrect,
    )

    # Log the review event.
    db.record_review_log(
        word=word,
        was_correct=was_correct,
        quality=quality,
        review_time=now_str,
        interval_before=interval_before,
        interval_after=new_interval,
        mastery_before=mastery_before,
        mastery_after=new_mastery,
        error_category=error_category,
    )

    # If the word has reached 'mastered', remove it from the wrong-word notebook.
    if new_mastery == MASTERY_MASTERED:
        db.remove_wrong_word_if_mastered(word)

    return new_mastery


# ===========================================================================
# Page routes (V1 preserved + V2 new)
# ===========================================================================

@app.route("/")
def index():
    """Dashboard page — V1 statistics + V2 analytics summary."""
    stats = db.get_practice_stats()
    wrong_count = db.get_wrong_word_count()
    total_words = len(vocab.VOCABULARY)

    total_q = stats.get("total_questions", 0)
    correct = stats.get("correct_answers", 0)
    accuracy = round(correct / total_q * 100, 1) if total_q > 0 else 0.0

    # V2 analytics data.
    mastery_dist = db.get_mastery_distribution()
    due_words = db.get_words_due_for_review()
    reviews_today = db.get_reviews_today()
    unlearned_count = total_words - sum(mastery_dist.values())

    return render_template(
        "index.html",
        total_words=total_words,
        total_questions=total_q,
        correct_answers=correct,
        incorrect_answers=stats.get("incorrect_answers", 0),
        accuracy=accuracy,
        wrong_count=wrong_count,
        # V2 analytics
        mastery_dist=mastery_dist,
        unlearned_count=unlearned_count,
        due_count=len(due_words),
        reviews_today=reviews_today,
    )


@app.route("/vocabulary")
def vocabulary_page():
    """Vocabulary library page — V2 adds mastery indicators."""
    keyword = request.args.get("q", "").strip()
    words = vocab.search_words(keyword)

    # Attach mastery state to each word.
    for w in words:
        review = db.get_word_review(w["word"])
        if review:
            w["mastery_level"] = review["mastery_level"]
            w["mastery_label"] = get_mastery_label(review["mastery_level"])
            w["next_review"] = review["next_review"]
            w["consecutive_correct"] = review["consecutive_correct"]
        else:
            w["mastery_level"] = MASTERY_UNLEARNED
            w["mastery_label"] = get_mastery_label(MASTERY_UNLEARNED)
            w["next_review"] = None
            w["consecutive_correct"] = 0

    return render_template("vocabulary.html", words=words, keyword=keyword)


@app.route("/practice")
def practice_page():
    """Practice page — V1 preserved."""
    mode = request.args.get("mode", "")
    return render_template("practice.html", mode=mode)


@app.route("/wrong-words")
def wrong_words_page():
    """Wrong-word notebook page — V2 adds targeted practice links."""
    wrong_words = db.get_wrong_words()

    # Attach mastery state to each wrong word.
    for ww in wrong_words:
        review = db.get_word_review(ww["word"])
        if review:
            ww["mastery_label"] = get_mastery_label(review["mastery_level"])
            ww["mastery_level"] = review["mastery_level"]
        else:
            ww["mastery_label"] = get_mastery_label(MASTERY_LEARNING)
            ww["mastery_level"] = MASTERY_LEARNING

    # Group by category for the UI.
    categories = {}
    for ww in wrong_words:
        cat = ww["error_category"] or "unrelated"
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    return render_template("wrong_words.html", wrong_words=wrong_words, categories=categories)


@app.route("/results")
def results_page():
    """Practice results page — V1 preserved."""
    results = session.get("last_results")
    if not results:
        return render_template("results.html", has_results=False)
    return render_template("results.html", has_results=True, results=results)


@app.route("/review")
def review_page():
    """V2 NEW: Daily review page — shows words due for spaced repetition."""
    due_words = db.get_words_due_for_review()
    # Attach vocabulary info to each due word.
    review_items = []
    for rw in due_words:
        entry = vocab.get_word_by_word(rw["word"])
        if entry:
            review_items.append({
                "word": rw["word"],
                "meaning": entry["meaning"],
                "pos": entry["pos"],
                "mastery_level": rw["mastery_level"],
                "mastery_label": get_mastery_label(rw["mastery_level"]),
                "next_review": rw["next_review"],
                "consecutive_correct": rw["consecutive_correct"],
                "review_interval_days": rw["review_interval_days"],
            })
    return render_template("review.html", due_words=review_items)


@app.route("/analytics")
def analytics_page():
    """V2 NEW: Learning analytics dashboard."""
    mastery_dist = db.get_mastery_distribution()
    total_words = len(vocab.VOCABULARY)
    unlearned_count = total_words - sum(mastery_dist.values())
    weak_words = db.get_weak_words(limit=10)
    trend = db.get_recent_accuracy_trend(days=7)
    reviews_today = db.get_reviews_today()
    due_words = db.get_words_due_for_review()
    recent_logs = db.get_review_logs(limit=20)

    # Attach vocabulary info to weak words.
    for ww in weak_words:
        entry = vocab.get_word_by_word(ww["word"])
        if entry:
            ww["meaning"] = entry["meaning"]
            ww["mastery_label"] = get_mastery_label(ww["mastery_level"])

    return render_template(
        "analytics.html",
        mastery_dist=mastery_dist,
        unlearned_count=unlearned_count,
        total_words=total_words,
        weak_words=weak_words,
        trend=trend,
        reviews_today=reviews_today,
        due_count=len(due_words),
        recent_logs=recent_logs,
    )


# ===========================================================================
# API routes — vocabulary (V1 preserved)
# ===========================================================================

@app.route("/api/words")
def api_words():
    keyword = request.args.get("q", "").strip()
    words = vocab.search_words(keyword)
    return jsonify({"words": words, "count": len(words)})


# ===========================================================================
# API routes — practice (V1 preserved + V2 spaced-repetition integration)
# ===========================================================================

@app.route("/api/practice/questions")
def api_practice_questions():
    """Generate random practice questions (V1 preserved)."""
    mode = request.args.get("mode", "en2cn")
    try:
        count = int(request.args.get("count", DEFAULT_QUESTION_COUNT))
    except (ValueError, TypeError):
        count = DEFAULT_QUESTION_COUNT
    count = max(1, min(count, 20))

    if mode not in ("en2cn", "cn2en"):
        return jsonify({"error": "无效的测试模式"}), 400

    all_words = vocab.get_all_words()
    selected = random.sample(all_words, min(count, len(all_words)))

    questions = []
    all_meanings = [w["meaning"] for w in all_words]

    for i, word_entry in enumerate(selected):
        if mode == "en2cn":
            correct_meaning = word_entry["meaning"]
            distractor_pool = [m for m in all_meanings if m != correct_meaning]
            distractors = random.sample(distractor_pool, min(CHOICE_COUNT - 1, len(distractor_pool)))
            options = distractors + [correct_meaning]
            random.shuffle(options)
            questions.append({
                "id": i, "type": "en2cn",
                "prompt": word_entry["word"], "pos": word_entry["pos"],
                "options": options, "correct_index": options.index(correct_meaning),
                "word": word_entry["word"], "correct_meaning": correct_meaning,
            })
        else:
            questions.append({
                "id": i, "type": "cn2en",
                "prompt": word_entry["meaning"], "pos": word_entry["pos"],
                "word": word_entry["word"], "correct_meaning": word_entry["meaning"],
                "confusable": word_entry.get("confusable", []),
            })

    return jsonify({"questions": questions, "mode": mode, "count": len(questions)})


@app.route("/api/practice/submit", methods=["POST"])
def api_practice_submit():
    """
    Submit practice answers (V1 preserved + V2 spaced-repetition updates).
    After analyzing each answer, the word's review state is updated using
    the SM-2-inspired algorithm.
    """
    data = request.get_json(silent=True)
    if not data or "answers" not in data:
        return jsonify({"error": "请求数据无效"}), 400

    mode = data.get("mode", "cn2en")
    answers = data["answers"]

    results_list = []
    correct_count = 0
    incorrect_count = 0

    for ans in answers:
        word = ans.get("word", "").strip()
        student_answer = ans.get("student_answer", "").strip()
        correct_meaning = ans.get("correct_meaning", "").strip()
        confusable = ans.get("confusable", [])

        if not word:
            continue

        if mode == "en2cn":
            analysis = analyze_meaning_answer(student_answer, correct_meaning)
            correct_answer_display = correct_meaning
        else:
            analysis = analyze_spelling_answer(student_answer, word, confusable)
            correct_answer_display = word

        was_correct = analysis["is_correct"]
        error_cat = analysis["error_category"]

        # V2: Update spaced-repetition state.
        new_mastery = update_word_review_state(word, was_correct, error_cat)

        if was_correct:
            correct_count += 1
        else:
            incorrect_count += 1
            db.record_wrong_word(
                word=word,
                student_answer=student_answer if student_answer else "(未作答)",
                correct_answer=correct_answer_display,
                error_category=error_cat,
            )

        results_list.append({
            "word": word,
            "student_answer": student_answer if student_answer else "(未作答)",
            "correct_answer": correct_answer_display,
            "is_correct": was_correct,
            "error_category": error_cat,
            "error_category_label": get_category_label(error_cat),
            "explanation": analysis["explanation"],
            "correct_meaning": correct_meaning,
            "new_mastery": get_mastery_label(new_mastery),
        })

    total = correct_count + incorrect_count
    db.update_practice_stats(total, correct_count, incorrect_count)

    accuracy = round(correct_count / total * 100, 1) if total > 0 else 0.0
    summary = {
        "mode": mode, "total": total,
        "correct": correct_count, "incorrect": incorrect_count,
        "accuracy": accuracy, "details": results_list,
    }
    session["last_results"] = summary
    return jsonify(summary)


# ===========================================================================
# API routes — V2 NEW: Review (spaced repetition)
# ===========================================================================

@app.route("/api/review/questions")
def api_review_questions():
    """
    V2 NEW: Generate practice questions from words due for review.
    Query params:
        mode — 'en2cn' or 'cn2en' (default 'cn2en')
        count — max questions (default 10)
    """
    mode = request.args.get("mode", "cn2en")
    try:
        count = int(request.args.get("count", DEFAULT_QUESTION_COUNT))
    except (ValueError, TypeError):
        count = DEFAULT_QUESTION_COUNT
    count = max(1, min(count, 20))

    if mode not in ("en2cn", "cn2en"):
        return jsonify({"error": "无效的测试模式"}), 400

    due_reviews = db.get_words_due_for_review()
    due_words = [vocab.get_word_by_word(r["word"]) for r in due_reviews]
    due_words = [w for w in due_words if w is not None]

    if not due_words:
        return jsonify({"questions": [], "mode": mode, "count": 0, "message": "没有需要复习的单词"})

    selected = random.sample(due_words, min(count, len(due_words)))
    questions = []
    all_meanings = [w["meaning"] for w in vocab.get_all_words()]

    for i, word_entry in enumerate(selected):
        if mode == "en2cn":
            correct_meaning = word_entry["meaning"]
            distractor_pool = [m for m in all_meanings if m != correct_meaning]
            distractors = random.sample(distractor_pool, min(CHOICE_COUNT - 1, len(distractor_pool)))
            options = distractors + [correct_meaning]
            random.shuffle(options)
            questions.append({
                "id": i, "type": "en2cn",
                "prompt": word_entry["word"], "pos": word_entry["pos"],
                "options": options, "correct_index": options.index(correct_meaning),
                "word": word_entry["word"], "correct_meaning": correct_meaning,
            })
        else:
            questions.append({
                "id": i, "type": "cn2en",
                "prompt": word_entry["meaning"], "pos": word_entry["pos"],
                "word": word_entry["word"], "correct_meaning": word_entry["meaning"],
                "confusable": word_entry.get("confusable", []),
            })

    return jsonify({"questions": questions, "mode": mode, "count": len(questions)})


# ===========================================================================
# API routes — V2 NEW: Targeted wrong-word practice
# ===========================================================================

@app.route("/api/wrong-words/practice-questions")
def api_wrong_word_practice_questions():
    """
    V2 NEW: Generate practice questions from the wrong-word notebook only.
    Query params:
        mode — 'en2cn' or 'cn2en' (default 'cn2en')
        category — filter by error category (optional)
        count — max questions (default 10)
    """
    mode = request.args.get("mode", "cn2en")
    category = request.args.get("category", "").strip()
    try:
        count = int(request.args.get("count", DEFAULT_QUESTION_COUNT))
    except (ValueError, TypeError):
        count = DEFAULT_QUESTION_COUNT
    count = max(1, min(count, 20))

    if mode not in ("en2cn", "cn2en"):
        return jsonify({"error": "无效的测试模式"}), 400

    # Get wrong words, optionally filtered by category.
    if category:
        wrong_words = db.get_wrong_words_by_category(category)
    else:
        wrong_words = db.get_wrong_words()

    # Look up full vocabulary entries for these words.
    word_entries = []
    for ww in wrong_words:
        entry = vocab.get_word_by_word(ww["word"])
        if entry:
            word_entries.append(entry)

    if not word_entries:
        return jsonify({"questions": [], "mode": mode, "count": 0, "message": "错词本中没有可练习的单词"})

    selected = random.sample(word_entries, min(count, len(word_entries)))
    questions = []
    all_meanings = [w["meaning"] for w in vocab.get_all_words()]

    for i, word_entry in enumerate(selected):
        if mode == "en2cn":
            correct_meaning = word_entry["meaning"]
            distractor_pool = [m for m in all_meanings if m != correct_meaning]
            distractors = random.sample(distractor_pool, min(CHOICE_COUNT - 1, len(distractor_pool)))
            options = distractors + [correct_meaning]
            random.shuffle(options)
            questions.append({
                "id": i, "type": "en2cn",
                "prompt": word_entry["word"], "pos": word_entry["pos"],
                "options": options, "correct_index": options.index(correct_meaning),
                "word": word_entry["word"], "correct_meaning": correct_meaning,
            })
        else:
            questions.append({
                "id": i, "type": "cn2en",
                "prompt": word_entry["meaning"], "pos": word_entry["pos"],
                "word": word_entry["word"], "correct_meaning": word_entry["meaning"],
                "confusable": word_entry.get("confusable", []),
            })

    return jsonify({"questions": questions, "mode": mode, "count": len(questions)})


# ===========================================================================
# API routes — wrong words (V1 preserved + V2 new)
# ===========================================================================

@app.route("/api/wrong-words")
def api_wrong_words():
    words = db.get_wrong_words()
    return jsonify({"wrong_words": words, "count": len(words)})


@app.route("/api/wrong-words/<int:word_id>", methods=["DELETE"])
def api_delete_wrong_word(word_id):
    deleted = db.delete_wrong_word(word_id)
    if deleted:
        return jsonify({"success": True})
    return jsonify({"error": "未找到该错词记录"}), 404


@app.route("/api/wrong-words/clear", methods=["POST"])
def api_clear_wrong_words():
    db.clear_wrong_words()
    return jsonify({"success": True})


# ===========================================================================
# API routes — statistics & analytics (V1 preserved + V2 new)
# ===========================================================================

@app.route("/api/stats")
def api_stats():
    stats = db.get_practice_stats()
    wrong_count = db.get_wrong_word_count()
    total_words = len(vocab.VOCABULARY)
    total_q = stats.get("total_questions", 0)
    correct = stats.get("correct_answers", 0)
    accuracy = round(correct / total_q * 100, 1) if total_q > 0 else 0.0
    mastery_dist = db.get_mastery_distribution()
    due_count = len(db.get_words_due_for_review())
    reviews_today = db.get_reviews_today()
    return jsonify({
        "total_words": total_words,
        "total_questions": total_q,
        "correct_answers": correct,
        "incorrect_answers": stats.get("incorrect_answers", 0),
        "accuracy": accuracy,
        "wrong_count": wrong_count,
        "mastery_distribution": mastery_dist,
        "due_count": due_count,
        "reviews_today": reviews_today,
    })


@app.route("/api/analytics")
def api_analytics():
    """V2 NEW: Detailed analytics data."""
    mastery_dist = db.get_mastery_distribution()
    total_words = len(vocab.VOCABULARY)
    unlearned_count = total_words - sum(mastery_dist.values())
    weak_words = db.get_weak_words(limit=10)
    trend = db.get_recent_accuracy_trend(days=7)
    reviews_today = db.get_reviews_today()
    due_count = len(db.get_words_due_for_review())
    return jsonify({
        "mastery_distribution": mastery_dist,
        "unlearned_count": unlearned_count,
        "total_words": total_words,
        "weak_words": weak_words,
        "trend": trend,
        "reviews_today": reviews_today,
        "due_count": due_count,
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    db.reset_all_data()
    return jsonify({"success": True})


# ===========================================================================
# Application startup
# ===========================================================================

db.init_db()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
