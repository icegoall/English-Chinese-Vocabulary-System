
# English-Chinese Vocabulary Learning System

A web-based English vocabulary learning system designed for Chinese middle-school students. It helps students learn vocabulary, practice spelling and meanings, analyze mistakes, and track learning progress.

This project contains two independent versions: Version 1 provides the core learning functions, while Version 2 introduces enhanced learning features such as spaced repetition and vocabulary mastery tracking.

## Features

### Version 1 — Core Functional System

- **Vocabulary Library:** Browse and search English vocabulary with Chinese meanings, parts of speech, and example sentences.
- **Vocabulary Practice:** Supports English-to-Chinese multiple-choice questions and Chinese-to-English spelling questions.
- **Intelligent Error Analysis:** Identifies spelling mistakes, confusing-word mistakes, and incorrect meanings.
- **Wrong-Word Notebook:** Automatically records incorrect answers and allows students to review or delete mistakes.
- **Learning Statistics:** Displays total questions, correct answers, incorrect answers, accuracy, and wrong-word counts.

### Version 2 — Enhanced Learning System

Includes all Version 1 features, with additional improvements:

- **Spaced Repetition:** Uses a simplified SM-2-inspired algorithm to schedule vocabulary reviews.
- **Vocabulary Mastery Tracking:** Tracks four learning states: Unlearned, Learning, Familiar, and Mastered.
- **Daily Review:** Automatically identifies words that are due for review.
- **Targeted Wrong-Word Practice:** Allows students to practice incorrect words by error category.
- **Learning Analytics:** Displays mastery distribution, daily review activity, accuracy trends, and frequently missed words.

> Note: Version 2 implements a simplified SM-2-inspired algorithm, not the complete standard SM-2 algorithm.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Testing | pytest, unittest |
| Python Version | Python 3.8+ |

## Project Structure

```text
English-Chinese-Vocabulary-System/
│
├── version1/
│   ├── app.py
│   ├── database.py
│   ├── vocabulary.py
│   ├── error_analyzer.py
│   ├── requirements.txt
│   ├── templates/
│   ├── static/
│   └── tests/
│
├── version2/
│   ├── app.py
│   ├── database.py
│   ├── vocabulary.py
│   ├── error_analyzer.py
│   ├── spaced_repetition.py
│   ├── requirements.txt
│   ├── templates/
│   ├── static/
│   └── tests/
│
├── submission/
│
├── check_servers.py
├── start_servers.py
└── start_servers_detached.py
```

## Installation

### Requirements

- Python 3.8 or later
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/icegoall/English-Chinese-Vocabulary-System.git
cd English-Chinese-Vocabulary-System
```

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r version1/requirements.txt
python -m pip install -r version2/requirements.txt
```

## Running the Applications

### Option 1: Start Both Versions

From the project root directory:

```powershell
python start_servers.py
```

The applications are available at:

- **Version 1:** http://127.0.0.1:5000
- **Version 2:** http://127.0.0.1:5001

To start both versions in detached processes on Windows:

```powershell
python start_servers_detached.py
```

### Option 2: Start Individually

**Version 1:**

```bash
cd version1
python app.py
```

Open http://127.0.0.1:5000.

**Version 2:**

```bash
cd version2
python run_port5001.py
```

Open http://127.0.0.1:5001.

## Running Tests

**Version 1:**

```bash
cd version1
python -m pytest tests/ -v
```

**Version 2:**

```bash
cd version2
python -m pytest tests/ -v
```

## Database

- Both versions use SQLite.
- Database files are created automatically when the applications start.
- Version 1 and Version 2 use separate databases.
- Learning records are stored locally.
- No external AI API is required for the core features.

## Documentation

For more detailed information, see:

- [Version 1 Documentation](version1/README.md)
- [Version 2 Documentation](version2/README.md)

## Project Purpose

The purpose of this project is to provide an interactive vocabulary learning platform that helps students improve English vocabulary retention through practice, error analysis, personalized review, and learning progress tracking.

---

**Project:** English-Chinese Vocabulary Learning System  
**Backend:** Python Flask  
**Database:** SQLite  
**Frontend:** HTML, CSS, JavaScript
