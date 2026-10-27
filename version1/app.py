"""
Flask application for the 中学生英语单词智能记忆与错词分析系统
(Middle-School English Vocabulary Intelligent Memory & Error Analysis System).

This is the main entry point. Run with:
    python app.py
Then open http://127.0.0.1:5000 in a browser.
"""

import random
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

import database as db
import vocabulary as vocab
from error_analyzer import (
    analyze_spelling_answer,
    analyze_meaning_answer,
    get_category_label,
)

app = Flask(__name__)
app.secret_key = "vocabulary-learning-system-v1-secret-key"

# Number of questions per practice session.
DEFAULT_QUESTION_COUNT = 10
# Number of multiple-choice options for English-to-Chinese mode.
CHOICE_COUNT = 4


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Dashboard page — shows learning statistics and navigation."""
    stats = db.get_practice_stats()
    wrong_count = db.get_wrong_word_count()
    total_words = len(vocab.VOCABULARY)

    # Calculate accuracy, guarding against division by zero.
    total_q = stats.get("total_questions", 0)
    correct = stats.get("correct_answers", 0)
    accuracy = round(correct / total_q * 100, 1) if total_q > 0 else 0.0

    return render_template(
        "index.html",
        total_words=total_words,
        total_questions=total_q,
        correct_answers=correct,
        incorrect_answers=stats.get("incorrect_answers", 0),
        accuracy=accuracy,
        wrong_count=wrong_count,
    )


@app.route("/vocabulary")
def vocabulary_page():
    """Vocabulary library page — browse and search all words."""
    keyword = request.args.get("q", "").strip()
    words = vocab.search_words(keyword)
    return render_template("vocabulary.html", words=words, keyword=keyword)


@app.route("/practice")
def practice_page():
    """Practice page — select a testing mode and answer questions."""
    mode = request.args.get("mode", "")
    return render_template("practice.html", mode=mode)


@app.route("/wrong-words")
def wrong_words_page():
    """Wrong-word notebook page — review and manage recorded mistakes."""
    wrong_words = db.get_wrong_words()
    return render_template("wrong_words.html", wrong_words=wrong_words)


@app.route("/results")
def results_page():
    """Practice results page — shows the outcome of the last practice session."""
    results = session.get("last_results")
    if not results:
        return render_template("results.html", has_results=False)
    return render_template("results.html", has_results=True, results=results)


# ---------------------------------------------------------------------------
# API routes — vocabulary
# ---------------------------------------------------------------------------

@app.route("/api/words")
def api_words():
    """Return vocabulary entries, optionally filtered by a search keyword."""
    keyword = request.args.get("q", "").strip()
    words = vocab.search_words(keyword)
    return jsonify({"words": words, "count": len(words)})


# ---------------------------------------------------------------------------
# API routes — practice
# ---------------------------------------------------------------------------

@app.route("/api/practice/questions")
def api_practice_questions():
    """
    Generate a set of random practice questions.

    Query parameters:
        mode — 'en2cn' (English→Chinese multiple choice) or
               'cn2en' (Chinese→English spelling input)
        count — number of questions (default 10, max 20)

    Returns JSON with a list of question objects.
    """
    mode = request.args.get("mode", "en2cn")
    try:
        count = int(request.args.get("count", DEFAULT_QUESTION_COUNT))
    except (ValueError, TypeError):
        count = DEFAULT_QUESTION_COUNT
    count = max(1, min(count, 20))

    if mode not in ("en2cn", "cn2en"):
        return jsonify({"error": "无效的测试模式"}), 400

    all_words = vocab.get_all_words()
    # Shuffle and pick the requested number of words.
    selected = random.sample(all_words, min(count, len(all_words)))

    questions = []
    all_meanings = [w["meaning"] for w in all_words]

    for i, word_entry in enumerate(selected):
        if mode == "en2cn":
            # English-to-Chinese: show English word, pick the correct Chinese meaning
            # plus distractors from other words' meanings.
            correct_meaning = word_entry["meaning"]
            distractor_pool = [m for m in all_meanings if m != correct_meaning]
            distractors = random.sample(
                distractor_pool, min(CHOICE_COUNT - 1, len(distractor_pool))
            )
            options = distractors + [correct_meaning]
            random.shuffle(options)
            questions.append({
                "id": i,
                "type": "en2cn",
                "prompt": word_entry["word"],
                "pos": word_entry["pos"],
                "options": options,
                "correct_index": options.index(correct_meaning),
                "word": word_entry["word"],
                "correct_meaning": correct_meaning,
            })
        else:
            # Chinese-to-English: show Chinese meaning, student types the English word.
            questions.append({
                "id": i,
                "type": "cn2en",
                "prompt": word_entry["meaning"],
                "pos": word_entry["pos"],
                "word": word_entry["word"],
                "correct_meaning": word_entry["meaning"],
                "confusable": word_entry.get("confusable", []),
            })

    return jsonify({"questions": questions, "mode": mode, "count": len(questions)})


@app.route("/api/practice/submit", methods=["POST"])
def api_practice_submit():
    """
    Submit practice answers for analysis.

    Expects JSON body:
        {
            "mode": "en2cn" | "cn2en",
            "answers": [
                {
                    "word": "accept",
                    "correct_meaning": "接受",
                    "student_answer": "except",   # typed word (cn2en) or selected meaning (en2cn)
                    "confusable": ["accept", "except"]  # only for cn2en
                },
                ...
            ]
        }

    Returns JSON with per-question analysis and an overall summary.
    Also records wrong answers in the database and updates statistics.
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
            # Meaning-selection mode.
            analysis = analyze_meaning_answer(student_answer, correct_meaning)
            correct_answer_display = correct_meaning
        else:
            # Spelling-input mode.
            analysis = analyze_spelling_answer(student_answer, word, confusable)
            correct_answer_display = word

        if analysis["is_correct"]:
            correct_count += 1
        else:
            incorrect_count += 1
            # Record the wrong answer in the database.
            db.record_wrong_word(
                word=word,
                student_answer=student_answer if student_answer else "(未作答)",
                correct_answer=correct_answer_display,
                error_category=analysis["error_category"],
            )

        results_list.append({
            "word": word,
            "student_answer": student_answer if student_answer else "(未作答)",
            "correct_answer": correct_answer_display,
            "is_correct": analysis["is_correct"],
            "error_category": analysis["error_category"],
            "error_category_label": get_category_label(analysis["error_category"]),
            "explanation": analysis["explanation"],
            "correct_meaning": correct_meaning,
        })

    # Update global practice statistics.
    total = correct_count + incorrect_count
    db.update_practice_stats(total, correct_count, incorrect_count)

    accuracy = round(correct_count / total * 100, 1) if total > 0 else 0.0
    summary = {
        "mode": mode,
        "total": total,
        "correct": correct_count,
        "incorrect": incorrect_count,
        "accuracy": accuracy,
        "details": results_list,
    }

    # Store in session so the /results page can display them.
    session["last_results"] = summary

    return jsonify(summary)


# ---------------------------------------------------------------------------
# API routes — wrong words
# ---------------------------------------------------------------------------

@app.route("/api/wrong-words")
def api_wrong_words():
    """Return all wrong-word entries as JSON."""
    words = db.get_wrong_words()
    return jsonify({"wrong_words": words, "count": len(words)})


@app.route("/api/wrong-words/<int:word_id>", methods=["DELETE"])
def api_delete_wrong_word(word_id):
    """Delete a wrong-word entry by ID."""
    deleted = db.delete_wrong_word(word_id)
    if deleted:
        return jsonify({"success": True})
    return jsonify({"error": "未找到该错词记录"}), 404


@app.route("/api/wrong-words/clear", methods=["POST"])
def api_clear_wrong_words():
    """Clear all wrong-word entries."""
    db.clear_wrong_words()
    return jsonify({"success": True})


# ---------------------------------------------------------------------------
# API routes — statistics
# ---------------------------------------------------------------------------

@app.route("/api/stats")
def api_stats():
    """Return current practice statistics and wrong-word count as JSON."""
    stats = db.get_practice_stats()
    wrong_count = db.get_wrong_word_count()
    total_words = len(vocab.VOCABULARY)
    total_q = stats.get("total_questions", 0)
    correct = stats.get("correct_answers", 0)
    accuracy = round(correct / total_q * 100, 1) if total_q > 0 else 0.0
    return jsonify({
        "total_words": total_words,
        "total_questions": total_q,
        "correct_answers": correct,
        "incorrect_answers": stats.get("incorrect_answers", 0),
        "accuracy": accuracy,
        "wrong_count": wrong_count,
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset all practice data and wrong-word records (for testing / fresh start)."""
    db.reset_all_data()
    return jsonify({"success": True})


# ---------------------------------------------------------------------------
# Application startup
# ---------------------------------------------------------------------------

def create_app():
    """Initialise the database and return the Flask app instance."""
    db.init_db()
    return app


# Initialise the database when the module is loaded.
db.init_db()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
