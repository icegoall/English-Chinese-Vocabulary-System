# Experiment 5 — Version 1: Core Functional System

## Project Name
中学生英语单词智能记忆与错词分析系统 (Middle-School English Vocabulary Intelligent Memory & Error Analysis System)

## Goal
Build a working English vocabulary learning application for middle-school students.

## 1. Project structure

Create the following structure inside the current workspace:

```
version1/
  app.py
  database.py
  vocabulary.py
  error_analyzer.py
  requirements.txt
  README.md
  templates/
    base.html
    index.html
    vocabulary.html
    practice.html
    wrong_words.html
    results.html
  static/
    css/
      style.css
    js/
      app.js
  tests/
    test_error_analyzer.py

submission/
  prompts/
    version1-prompt.md
```

Keep all Version 1 code inside the version1 directory. Do not modify files outside the current workspace.

## 2. Technology

- Backend: Python Flask
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Vocabulary data: built-in Python data
- No external AI API or paid services.
- No login or online leaderboard.

## 3. Core features

### A. Vocabulary library (词汇库)

Build a built-in vocabulary collection suitable for middle-school students.

Each word should contain:
- English word
- Chinese meaning
- Part of speech
- Example sentence
- Chinese example translation
- Optional confusing-word group

Include at least 40 useful vocabulary entries.

Allow students to browse and search words.

### B. Vocabulary self-test (单词自测)

Provide two testing modes:

1. English-to-Chinese meaning selection.
2. Chinese-to-English spelling input.

Randomize questions and provide immediate feedback.

### C. Intelligent error analysis (错词分析)

Implement three types of error identification:

1. 拼写错误 — spelling mistakes, using normalized comparison and basic edit-distance analysis.
2. 形近词混淆 — confusable-word mistakes, identifying when the entered word matches another vocabulary entry in a known confusing group.
3. 词义答错 — incorrect Chinese meaning selection when the English word is correct.

Explain the identified error to the student and show the correct answer.

Do not incorrectly classify ordinary unrelated answers as confusable-word mistakes.

### D. Wrong-word notebook (错词本)

Automatically record incorrect answers in SQLite.

Store:
- Vocabulary word
- Student answer
- Correct answer
- Error category
- Number of mistakes
- Last mistake time

Provide a page where students can review their wrong words and practise them again.

### E. Basic learning statistics

Display:
- Total vocabulary learned
- Total practice questions
- Correct answers
- Incorrect answers
- Accuracy percentage
- Number of words in the wrong-word notebook

Show simple progress cards on the dashboard.

## 4. Interface requirements

Create a professional, clean, modern interface suitable for middle-school students.

Use Chinese for all interface text.

Include:
- Dashboard
- Vocabulary library
- Practice page
- Wrong-word notebook
- Practice results page

Use responsive layouts for computers and mobile devices.

## 5. Important implementation rules

- Use SQLite to persist wrong-word records and practice statistics.
- Initialize the database automatically if it does not exist.
- Validate user inputs.
- Handle empty answers and invalid requests gracefully.
- Keep backend and frontend logic organized.
- Do not use fake statistics.
- Make every button and navigation link functional.
- Include useful comments in the code.

## 6. Testing and verification

Create tests for the three error categories.

Test at least:
- Correct spelling
- Capitalization differences
- Common spelling mistakes
- Known confusing-word pairs
- Incorrect Chinese meaning selection
- Unrelated incorrect answers
- Wrong-word recording

Run the tests if the environment allows it. Fix errors you discover.

## 7. Documentation and submission evidence

Save this complete implementation prompt in:

```
submission/prompts/version1-prompt.md
```

Create README.md explaining:
- Project features
- Project structure
- Environment installation
- How to start the Flask server
- How to access the application in a browser
- How to run tests

Do not initialize Git or push anything to GitCode yet.

At the end, report:
1. Files created.
2. Implemented features.
3. Tests performed and actual results.
4. Any remaining limitations.

Please implement the application directly in the workspace rather than returning code snippets only.
