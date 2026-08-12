# Python Agent AI — Logical Flow

## 📋 Project Overview
A multi-tool ReAct agent combining data analysis (Pandas), PDF reading, web scraping, and note-taking into a single conversational interface using GPT-4o-mini.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  Python Agent AI                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  User Natural Language Query                                 │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  ReAct Agent (GPT-4o-mini)            │                   │
│  │                                       │                   │
│  │  Reasoning Loop:                      │                   │
│  │  Think → Act → Observe → Repeat       │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Select Tool Based on Query           │                   │
│  └──────────┬───────────────────────────┘                    │
│             │                                                │
│        ┌────┼────────┬──────────┬──────────┐                 │
│        ▼    ▼        ▼          ▼          ▼                 │
│                                                              │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Pandas  │ │   PDF    │ │  Coffee  │ │   Note   │         │
│  │ Query   │ │  Reader  │ │ Scraper  │ │  Engine  │         │
│  │ Engine  │ │          │ │          │ │          │         │
│  │         │ │ pdf.py   │ │ coffee_  │ │ note_    │         │
│  │ CSV/DF  │ │          │ │ scraper  │ │ engine   │         │
│  │ analysis│ │ Canada   │ │ .py      │ │ .py      │         │
│  │         │ │ document │ │          │ │          │         │
│  │ prompts │ │ QA       │ │ Google   │ │ File     │         │
│  │ .py     │ │          │ │ Maps via │ │ based    │         │
│  │ (query  │ │          │ │ Scrape-  │ │ persist  │         │
│  │ instrs) │ │          │ │ less API │ │ -ence    │         │
│  └────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘         │
│       │           │            │            │                │
│       └───────────┼────────────┼────────────┘                │
│                   │            │                             │
│                   └──────┬─────┘                             │
│                          │                                   │
│                          ▼                                   │
│              Tool Execution Result                           │
│                          │                                   │
│                          ▼                                   │
│              Agent Synthesizes Response                      │
│              (May chain multiple tools)                      │
│                          │                                   │
│                          ▼                                   │
│              Display Final Answer                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

