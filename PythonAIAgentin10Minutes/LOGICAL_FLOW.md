# Python AI Agent in 10 Minutes — Logical Flow

## 📋 Project Overview
A lightweight data generation agent using LangGraph ReAct pattern that creates synthetic user datasets through natural language with JSON persistence and conversation memory.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│           Python AI Agent in 10 Minutes                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  User Describes Data Needs                                   │
│  e.g., "Generate 50 users with names and emails"            │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  LangGraph ReAct Agent                │                   │
│  │                                       │                   │
│  │  Conversation History (Memory)        │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Determine Approach                   │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Tool Selection                       │                   │
│  └──────────┬───────────────────────────┘                    │
│             │                                                │
│        ┌────┼────────────┐                                   │
│        ▼    ▼            ▼                                   │
│                                                              │
│  ┌──────────────┐ ┌───────────┐ ┌──────────┐                │
│  │ generate_    │ │ write_    │ │ read_    │                │
│  │ sample_     │ │ json()    │ │ json()   │                │
│  │ users()      │ │           │ │          │                │
│  │              │ │ Save data │ │ Load data│                │
│  │ Create fake  │ │ to .json  │ │ from     │                │
│  │ user data    │ │ file      │ │ .json    │                │
│  │ with custom  │ │           │ │ file     │                │
│  │ parameters   │ │           │ │          │                │
│  └──────┬───────┘ └─────┬─────┘ └────┬─────┘                │
│         │               │            │                       │
│         └───────────────┼────────────┘                       │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────┐                    │
│  │  Agent Response                       │                   │
│  │  ├── Generated data summary           │                   │
│  │  └── File saved confirmation          │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  Display to User                                             │
│                 │                                            │
│                 ▼                                            │
│  Maintain conversation memory                                │
│  for follow-up requests                                      │
│  e.g., "Add phone numbers to those users"                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

