# DevLaunch Discord Bot — Logical Flow

## 📋 Project Overview
A Discord server analytics bot that captures message metadata, stores in PostgreSQL, and provides AI-powered commands for history, summarization, and Q&A.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│               DevLaunch Discord Bot                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ══════ MESSAGE CAPTURE FLOW ══════                          │
│                                                              │
│  Any Discord Message                                         │
│       │                                                      │
│       ▼                                                      │
│  on_message() Event Handler                                  │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  Database Operations                  │                   │
│  │  ├── ensure_channel_exists()          │                   │
│  │  ├── ensure_user_exists()             │                   │
│  │  └── insert_message()                 │                   │
│  │       ├── content                     │                   │
│  │       ├── author metadata             │                   │
│  │       ├── channel info                │                   │
│  │       └── timestamp                   │                   │
│  └──────────────────────────────────────┘                    │
│       │                                                      │
│       ▼                                                      │
│  PostgreSQL (Channel, User, Message tables)                  │
│                                                              │
│  ══════ COMMAND FLOW ══════                                  │
│                                                              │
│  User types command in Discord                               │
│       │                                                      │
│       ├──→ !history [filters]                                │
│       │         │                                            │
│       │         ▼                                            │
│       │    Parse Filters                                     │
│       │    (user_id, channel_id, since)                      │
│       │         │                                            │
│       │         ▼                                            │
│       │    db.get_messages(filters)                           │
│       │         │                                            │
│       │         ▼                                            │
│       │    Format as Discord Embed                           │
│       │    (4000 char limit)                                 │
│       │                                                      │
│       ├──→ !summarize [filters]                              │
│       │         │                                            │
│       │         ▼                                            │
│       │    db.get_messages(filters)                           │
│       │         │                                            │
│       │         ▼                                            │
│       │    ┌──────────────────────┐                           │
│       │    │  OpenAI LLM          │                          │
│       │    │  summarize_messages() │                          │
│       │    │  ├── Topics          │                          │
│       │    │  ├── Decisions       │                          │
│       │    │  └── Sentiment       │                          │
│       │    └──────────┬───────────┘                           │
│       │               │                                      │
│       │               ▼                                      │
│       │    Discord Embed with Summary                        │
│       │                                                      │
│       └──→ !ask [question] [filters]                         │
│                 │                                            │
│                 ▼                                            │
│            db.get_messages(filters)                           │
│                 │                                            │
│                 ▼                                            │
│            ┌──────────────────────┐                           │
│            │  OpenAI LLM          │                          │
│            │  ask_question()      │                          │
│            │  (context-bound QA)  │                          │
│            └──────────┬───────────┘                           │
│                       │                                      │
│                       ▼                                      │
│            Discord Embed with Answer                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

