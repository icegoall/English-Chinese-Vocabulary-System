# 中学生英语单词智能记忆与错词分析系统 V2

> Version 2 — 智能间隔复习与学习分析增强版

## 项目简介

本项目是一个面向中学生的英语单词学习 Web 应用，基于 Version 1 的核心功能，新增了智能间隔复习算法、单词掌握度追踪、错词专项练习和学习分析仪表盘等功能。系统使用 Flask + SQLite + HTML/CSS/JS 技术栈，无需外部 AI 接口或登录系统。

---

## Version 2 相比 Version 1 的改进

### 1. 智能间隔复习（SM-2 简化算法）

- 实现了基于 SM-2 算法的简化间隔复习调度（`spaced_repetition.py`）
- 每个单词追踪：掌握度等级、连续正确次数、复习间隔（天）、难度系数（Ease Factor）、上次复习时间、下次计划复习时间
- **答对**时增加复习间隔，**答错**时重置间隔为 1 天并降低难度系数
- 新单词自动进入学习队列，到期单词自动出现在每日复习页面
- 所有调度信息持久化到 SQLite，应用重启后不丢失

> 注意：本系统实现的是 SM-2 的**简化版本**，并非完整的 SM-2 标准。简化点包括：仅使用两级质量评分（正确 q=5，错误 q=2），而非完整的 0-5 六级评分。

### 2. 错词专项练习

- 新增 `/api/wrong-words/practice-questions` 接口，仅从错词本中生成练习题
- 支持**按错误类型筛选**练习：拼写错误、形近词混淆、词义答错、其他错误
- 支持**练习全部错词**或**复习特定单词**
- 当单词达到「已掌握」等级时，自动从错词本中移除

### 3. 单词掌握度追踪

- 每个单词拥有四种掌握状态：
  - ⚪ **未学习**（unlearned）：从未练习过
  - 🟡 **学习中**（learning）：连续正确 < 2 次
  - 🔵 **基本掌握**（familiar）：连续正确 ≥ 2 次，但尚未达到掌握标准
  - 🟢 **已掌握**（mastered）：连续正确 ≥ 3 次 且 复习间隔 ≥ 7 天
- 词汇库页面显示每个单词的掌握度徽章和下次复习日期
- 答错时掌握度回退到「学习中」

### 4. 学习分析仪表盘

- 新增 `/analytics` 页面，提供全面的学习数据分析
- **掌握度分布**：未学习 / 学习中 / 基本掌握 / 已掌握 的单词数量
- **今日概况**：待复习单词数、今日已复习次数、词汇总量
- **近 7 天正确率趋势**：柱状图展示每日正确率
- **薄弱单词**：按错误率排序的高频错误单词
- **最近复习记录**：展示最近的复习事件及掌握度变化
- 所有统计数据来自真实 SQLite 记录，不使用任何模拟数据

---

## 安装要求

- Python 3.8 或更高版本
- pip（Python 包管理器）

## 安装依赖

```bash
cd version2
pip install -r requirements.txt
```

`requirements.txt` 中仅包含一个依赖：`Flask==3.0.0`

## 初始化数据库

数据库会在应用启动时**自动创建**，无需手动初始化。

数据库文件为 `vocabulary_v2.db`，位于 `version2/` 目录下，与 Version 1 的 `vocabulary.db` 相互独立。

如需重置所有数据，可调用 `POST /api/reset` 接口，或直接删除 `vocabulary_v2.db` 文件后重新启动应用。

## 启动 Flask 应用

```bash
cd version2
python app.py
```

服务器启动后监听 `http://127.0.0.1:5000`。

## 浏览器访问

启动服务器后，在浏览器中打开：

```
http://127.0.0.1:5000
```

### 页面说明

| 页面 | URL | 说明 |
|------|-----|------|
| 首页（仪表盘） | `/` | 学习统计 + 掌握度分布 + 今日复习概览 |
| 词汇库 | `/vocabulary` | 浏览和搜索单词，显示掌握度 |
| 单词自测 | `/practice` | 选择测试模式，随机出题 |
| 每日复习 | `/review` | V2 新增：到期单词的间隔复习 |
| 错词本 | `/wrong-words` | 错词管理 + 分类专项练习 |
| 测试结果 | `/results` | 查看上次测试的详细分析 |
| 学习分析 | `/analytics` | V2 新增：掌握度分布与学习趋势 |

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/words` | GET | 获取词汇列表（支持搜索） |
| `/api/practice/questions` | GET | 生成随机练习题目 |
| `/api/practice/submit` | POST | 提交答案并分析 |
| `/api/review/questions` | GET | V2 新增：生成到期复习题目 |
| `/api/wrong-words/practice-questions` | GET | V2 新增：从错词本生成专项练习题 |
| `/api/wrong-words` | GET | 获取错词列表 |
| `/api/wrong-words/<id>` | DELETE | 删除单条错词 |
| `/api/wrong-words/clear` | POST | 清空错词本 |
| `/api/stats` | GET | 获取统计数据 |
| `/api/analytics` | GET | V2 新增：获取学习分析数据 |
| `/api/reset` | POST | 重置所有数据 |

---

## 数据库结构

数据库使用 SQLite，文件名为 `vocabulary_v2.db`，包含 4 张表：

| 表名 | 版本 | 说明 |
|------|------|------|
| `wrong_words` | V1 保留 | 错词本：单词、学生答案、正确答案、错误类型、错误次数、最近错误时间 |
| `practice_stats` | V1 保留 | 全局练习统计：总题数、正确数、错误数 |
| `word_reviews` | V2 新增 | 间隔复习状态：掌握度、连续正确、间隔天数、难度系数、下次复习时间等 |
| `review_log` | V2 新增 | 复习历史日志：每次复习的结果、质量评分、间隔变化、掌握度变化 |

所有表使用 `CREATE TABLE IF NOT EXISTS` 创建，确保安全的非破坏性迁移，不会删除已有数据。

---

## 运行测试

```bash
cd version2
python -m pytest tests/ -v
```

也可以使用 unittest 运行：

```bash
python -m unittest discover tests -v
```

### 测试文件说明

| 测试文件 | 说明 | 测试内容 |
|----------|------|----------|
| `test_error_analyzer.py` | V1 保留 | 拼写错误、形近词混淆、词义答错、不相关答案、错词记录 |
| `test_spaced_repetition.py` | V2 新增 | 间隔计算、难度系数更新、到期日期判断、掌握度判定 |
| `test_database.py` | V2 新增 | 数据库增删改查、持久化验证、安全迁移、复习日志 |
| `test_mastery.py` | V2 新增 | 掌握度状态转换、完整生命周期、专项练习、仪表盘统计 |

---

## 项目结构

```
version2/
├── app.py                      # Flask 应用主文件（所有路由和 API）
├── database.py                 # SQLite 数据库管理（V1 表 + V2 新增表）
├── vocabulary.py               # 内置词汇库（48 个单词）
├── error_analyzer.py           # 智能错词分析（V1 保留）
├── spaced_repetition.py        # V2 新增：SM-2 简化间隔复习算法
├── requirements.txt            # Python 依赖
├── README.md                   # 本文件
├── templates/
│   ├── base.html               # 基础模板（含导航栏）
│   ├── index.html              # 首页仪表盘（统计 + 掌握度 + 复习概览）
│   ├── vocabulary.html         # 词汇库（含掌握度徽章）
│   ├── practice.html           # 单词自测页面
│   ├── review.html             # V2 新增：每日复习页面
│   ├── wrong_words.html        # 错词本（含分类专项练习）
│   ├── results.html            # 测试结果（含掌握度变化）
│   └── analytics.html          # V2 新增：学习分析仪表盘
├── static/
│   ├── css/
│   │   └── style.css           # 响应式样式表（V1 + V2 扩展）
│   └── js/
│       └── app.js              # 共享 JavaScript
└── tests/
    ├── test_error_analyzer.py  # V1 保留：错词分析测试
    ├── test_spaced_repetition.py  # V2 新增：间隔复习算法测试
    ├── test_database.py        # V2 新增：数据库持久化测试
    └── test_mastery.py         # V2 新增：掌握度转换测试
```

---

## 技术栈

- **后端**：Python Flask
- **数据库**：SQLite（自动初始化，V2 独立数据文件）
- **前端**：HTML、CSS、JavaScript（原生，无框架）
- **词汇数据**：内置 Python 数据结构（48 个单词）
- **测试**：Python unittest / pytest

## 与 Version 1 的兼容性

- Version 2 代码完全独立，位于 `version2/` 目录
- 不修改 `version1/` 目录中的任何文件
- 使用独立的数据库文件 `vocabulary_v2.db`，不影响 V1 的 `vocabulary.db`
- 保留所有 V1 功能：词汇浏览搜索、单词自测、错词分析、错词本、学习统计
