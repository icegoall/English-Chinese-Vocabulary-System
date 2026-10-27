# 中学生英语单词智能记忆与错词分析系统

> Version 1 — Core Functional System

A web-based English vocabulary learning application designed for Chinese middle-school students. The system provides vocabulary browsing, self-testing, intelligent error analysis, a wrong-word notebook, and learning statistics.

## 项目功能 (Features)

### A. 词汇库 (Vocabulary Library)
- 45 built-in vocabulary entries suitable for middle-school students
- Each word includes: English word, Chinese meaning, part of speech, example sentence, Chinese example translation, and optional confusing-word group
- Browse and search words by English text or Chinese meaning

### B. 单词自测 (Vocabulary Self-Test)
- **英译中 (English→Chinese):** Multiple-choice — select the correct Chinese meaning for a given English word
- **中译英 (Chinese→English):** Spelling input — type the English word for a given Chinese meaning
- Questions are randomized; immediate feedback after submission

### C. 智能错词分析 (Intelligent Error Analysis)
Three error categories are identified:
1. **拼写错误 (Spelling errors)** — detected via normalized comparison and Levenshtein edit-distance analysis (edit distance ≤ 2)
2. **形近词混淆 (Confusable-word mistakes)** — detected when the entered word exactly matches a known confusable partner (e.g., "except" instead of "accept")
3. **词义答错 (Meaning errors)** — detected when the wrong Chinese meaning is selected in English→Chinese mode

Unrelated answers (large edit distance, no confusable match) are recorded as wrong but are **not** misclassified as confusable mistakes.

### D. 错词本 (Wrong-Word Notebook)
- Automatically records incorrect answers in SQLite
- Stores: vocabulary word, student answer, correct answer, error category, mistake count, last mistake time
- Review and delete entries; clear the entire notebook

### E. 学习统计 (Learning Statistics)
- Total vocabulary count
- Total practice questions
- Correct / incorrect answer counts
- Accuracy percentage
- Number of words in the wrong-word notebook

## 项目结构 (Project Structure)

```
version1/
├── app.py                  # Flask application with all routes and API endpoints
├── database.py             # SQLite database management (wrong words + stats)
├── vocabulary.py           # Built-in vocabulary data (45 entries)
├── error_analyzer.py       # Intelligent error analysis (spelling, confusable, meaning)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── templates/
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Dashboard with statistics
│   ├── vocabulary.html     # Vocabulary library (browse + search)
│   ├── practice.html       # Practice page (mode selection + quiz)
│   ├── wrong_words.html    # Wrong-word notebook
│   └── results.html        # Practice results with detailed analysis
├── static/
│   ├── css/
│   │   └── style.css       # Professional, responsive stylesheet
│   └── js/
│       └── app.js          # Shared client-side JavaScript
└── tests/
    └── test_error_analyzer.py  # Unit tests for error analysis + database
```

## 环境安装 (Environment Setup)

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Navigate to the `version1` directory:
   ```bash
   cd version1
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   This installs Flask, the only external dependency.

## 启动服务器 (Starting the Flask Server)

From the `version1` directory, run:

```bash
python app.py
```

The server will start on `http://127.0.0.1:5000`.

The SQLite database (`vocabulary.db`) is created automatically in the `version1` directory on first run.

## 访问应用 (Accessing the Application)

1. Start the Flask server as described above
2. Open a web browser
3. Go to: **http://127.0.0.1:5000**

### Pages
| Page | URL | Description |
|------|-----|-------------|
| 首页 (Dashboard) | `/` | Learning statistics and navigation |
| 词汇库 (Vocabulary) | `/vocabulary` | Browse and search all words |
| 单词自测 (Practice) | `/practice` | Select mode and take a quiz |
| 错词本 (Wrong Words) | `/wrong-words` | Review and manage mistakes |
| 测试结果 (Results) | `/results` | View last practice results |

## 运行测试 (Running Tests)

From the `version1` directory, run:

```bash
python -m pytest tests/ -v
```

Or using the built-in unittest runner:

```bash
python -m unittest tests.test_error_analyzer -v
```

The test suite covers:
- Levenshtein edit-distance computation
- Correct spelling recognition
- Capitalization difference handling
- Common spelling mistakes
- Known confusable-word pairs
- Incorrect Chinese meaning selection
- Unrelated answers (not misclassified as confusable)
- Wrong-word database recording, incrementing, and deletion
- Practice statistics updates

## 技术栈 (Technology Stack)

- **Backend:** Python Flask
- **Database:** SQLite (automatic initialization)
- **Frontend:** HTML, CSS, JavaScript (vanilla, no frameworks)
- **Vocabulary Data:** Built-in Python data structures
- **Testing:** Python unittest / pytest

No external AI API, paid services, login, or online leaderboard required.
