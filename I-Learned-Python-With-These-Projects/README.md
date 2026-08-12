# I Learned Python With These Projects

Three beginner-friendly Python projects for learning fundamentals through hands-on practice: a **trivia quiz**, a **password generator**, and a **todo list manager**.

---

## 📋 Projects Overview

| # | Project | File | Description |
|---|---------|------|-------------|
| 1 | **Python Trivia Quiz** | `project1.py` | Interactive multiple-choice quiz game |
| 2 | **Password Generator** | `project2.py` | Customizable password creation tool |
| 3 | **Todo List Manager** | `project3.py` | JSON-based task management CLI |

---

## 🚀 Getting Started

No dependencies required — just Python 3.10+.

```bash
python project1.py   # Trivia Quiz
python project2.py   # Password Generator
python project3.py   # Todo List
```

---

## 📖 Project Details

### Project 1 — Python Trivia Quiz (`project1.py`)
**What it does:** Interactive multiple-choice quiz with scoring.

**Logic Flow:**
1. Questions randomly selected from a pool
2. User selects answer (A/B/C/D)
3. Answer validated against correct answer
4. Score tracked and displayed at end

**Key Concepts:** Lists, dictionaries, random module, input validation, loops

---

### Project 2 — Password Generator (`project2.py`)
**What it does:** Generate secure passwords with customizable options.

**Logic Flow:**
1. User specifies password length
2. User toggles: uppercase, digits, special characters
3. Character pool assembled based on selections
4. Random characters selected from pool
5. Generated password displayed

**Key Concepts:** String module, random module, conditional logic, string concatenation

---

### Project 3 — Todo List Manager (`project3.py`)
**What it does:** Persistent todo list with JSON file storage.

**Logic Flow:**
1. Load existing todos from `todo_list.json`
2. Menu: Add / View / Mark Complete / Exit
3. User actions modify the todo list
4. Changes saved to JSON after each action

**Key Concepts:** File I/O, JSON serialization, while loops, list manipulation

---

## 📁 File Structure
```
I-Learned-Python-With-These-Projects/
├── project1.py          # Trivia Quiz
├── project2.py          # Password Generator
├── project3.py          # Todo List Manager
└── todo_list.json       # Persistent todo storage
```

---

## 📝 License
Educational project — use freely for learning and reference.
