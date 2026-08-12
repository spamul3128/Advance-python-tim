# I Learned Python With These Projects — Logical Flow

## 📋 Project Overview
Three beginner Python projects: a trivia quiz game, a password generator, and a JSON-based todo list manager.

---

## 🔄 Project 1: Trivia Quiz Game

```
┌─────────────────────────────────────────────────────┐
│               Trivia Quiz Game                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Load Questions Dictionary                          │
│       │                                             │
│       ▼                                             │
│  Randomly Select 5 Questions                        │
│       │                                             │
│       ▼                                             │
│  ┌─────────────────────────┐                        │
│  │  For each question:     │                        │
│  │       │                 │                        │
│  │       ▼                 │                        │
│  │  Display Question       │                        │
│  │       │                 │                        │
│  │       ▼                 │                        │
│  │  Get User Answer        │                        │
│  │       │                 │                        │
│  │       ▼                 │                        │
│  │  Validate Answer        │                        │
│  │  ├── Correct → score+1  │                        │
│  │  └── Wrong → show answer│                        │
│  └─────────────────────────┘                        │
│       │                                             │
│       ▼                                             │
│  Display Final Score (X/5)                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Project 2: Password Generator

```
┌─────────────────────────────────────────────────────┐
│             Password Generator                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Get User Preferences                               │
│  ├── Password length                                │
│  ├── Include uppercase? (y/n)                       │
│  ├── Include digits? (y/n)                          │
│  └── Include special chars? (y/n)                   │
│       │                                             │
│       ▼                                             │
│  Build Character Pool                               │
│  ├── Always: lowercase (a-z)                        │
│  ├── Optional: uppercase (A-Z)                      │
│  ├── Optional: digits (0-9)                         │
│  └── Optional: special (!@#$...)                    │
│       │                                             │
│       ▼                                             │
│  Ensure Required Characters                         │
│  (At least one from each selected type)             │
│       │                                             │
│       ▼                                             │
│  Random Selection for remaining length              │
│       │                                             │
│       ▼                                             │
│  Shuffle All Characters                             │
│       │                                             │
│       ▼                                             │
│  Display Generated Password                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Project 3: Todo List Manager

```
┌─────────────────────────────────────────────────────┐
│              Todo List Manager                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Load tasks from todo_list.json                     │
│       │                                             │
│       ▼                                             │
│  ┌─────────────────────────┐                        │
│  │   Display Menu          │  ◄────────┐            │
│  │   1. Add Task           │           │            │
│  │   2. View Tasks         │           │            │
│  │   3. Complete Task      │           │            │
│  │   4. Exit               │           │            │
│  └──────────┬──────────────┘           │            │
│             │                          │            │
│        ┌────┼────┬────┐                │            │
│        ▼    ▼    ▼    ▼                │            │
│                                        │            │
│  1. Add:                               │            │
│     Input task text                    │            │
│     Append to list                     │            │
│     Save to JSON ──────────────────────┤            │
│                                        │            │
│  2. View:                              │            │
│     Display all tasks                  │            │
│     Show completion status ────────────┤            │
│                                        │            │
│  3. Complete:                          │            │
│     Select task number                 │            │
│     Mark as done                       │            │
│     Save to JSON ──────────────────────┘            │
│                                                     │
│  4. Exit: Save & Quit                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

