# Experiment 5 — Version 2: Intelligent Improvements

We have completed and tested Version 1 of the English Vocabulary Memory and Error Analysis System.

Now implement Version 2 as an independent iteration.

IMPORTANT:
- Do NOT modify or overwrite the existing version1 folder.
- Create a separate version2 folder by using Version 1 as the starting point.
- Preserve all Version 1 functionality.
- Make meaningful improvements rather than only changing the interface.
- Do not push anything to GitCode.

## 1. Main improvements

### A. Intelligent spaced repetition (智能间隔复习)

Implement a simplified SM-2-inspired spaced-repetition algorithm.

Each vocabulary word should track:
- Current mastery level
- Consecutive correct reviews
- Review interval in days
- Ease factor or equivalent difficulty value
- Last reviewed time
- Next scheduled review time

Rules:
- A correct answer increases the review interval.
- An incorrect answer reduces mastery and schedules an earlier review.
- New words enter the learning queue.
- Words due for review appear automatically.
- Review scheduling must persist in SQLite.

Do not claim to implement the complete SM-2 standard unless it actually does.

### B. Targeted wrong-word practice (错词专项练习)

Improve the existing wrong-word notebook.

Add a function that generates practice questions using only the student's recorded wrong words.

Allow students to:
- Practise all wrong words.
- Practise by error category.
- Review a specific word.
- Remove a word after successful mastery according to a clear rule.

Do not simply redirect the user to general practice.

### C. Vocabulary mastery tracking (单词掌握度)

Assign each word a mastery state:
- 未学习
- 学习中
- 基本掌握
- 已掌握

Update the state based on actual practice history and spaced-repetition performance.

Show mastery status in the vocabulary library.

### D. Learning analytics dashboard (学习分析)

Add useful learning statistics:
- Words due for review today.
- Words reviewed today.
- Words currently being learned.
- Words mastered.
- Weak vocabulary.
- Recent accuracy trends.

Use actual SQLite records. Never generate fake statistics.

## 2. Database and compatibility

- Keep Version 2 data independent from Version 1.
- Add database migrations safely.
- Preserve existing Version 1 code and data.
- Avoid deleting existing records.
- Ensure all scheduling information survives application restarts.

## 3. Interface improvements

Maintain the existing Chinese interface and responsive design.

Add:
- A dedicated daily-review page.
- A targeted wrong-word practice mode.
- Mastery indicators.
- A learning analytics section.
- Clear next-review dates for each word.

## 4. Testing

Add tests for:
- First-time review scheduling.
- Correct-answer interval increases.
- Incorrect-answer interval resets or decreases.
- Review due-date calculation.
- Persistence after application restart.
- Targeted wrong-word practice.
- Mastery-level transitions.
- Dashboard statistics.

Run all Version 1 and Version 2 tests where possible. Fix regressions without modifying version1.

## 5. Submission records

Save the complete Version 2 implementation prompt to:

submission/prompts/version2-prompt.md

Create a Version 2 README.md documenting the improvements and how to run it.

Keep all Version 2 application files inside version2/.

At the end, report:
- Files created or modified.
- New features.
- Database changes.
- Tests performed and actual results.
- Remaining limitations.

Implement the code directly in the workspace.
