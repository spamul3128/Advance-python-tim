# Advanced Langflow Web Agent — Logical Flow

## 📋 Project Overview
A multi-source research agent that searches Google, Bing, and Reddit in parallel, analyzes results individually using GPT, and synthesizes a comprehensive final answer.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│               Advanced Langflow Web Agent                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  User Research Query                                         │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────── PARALLEL SEARCH ──────────────┐            │
│  │                                               │           │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────┐  │           │
│  │  │  Google   │  │   Bing   │  │  Reddit    │  │           │
│  │  │  Search   │  │  Search  │  │  Search    │  │           │
│  │  │(BrightData│  │(BrightData│ │(BrightData)│  │           │
│  │  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │           │
│  │       │              │              │         │           │
│  └───────┼──────────────┼──────────────┼─────────┘           │
│          │              │              │                      │
│          │              │              ▼                      │
│          │              │    ┌──────────────────┐             │
│          │              │    │ Filter Reddit    │             │
│          │              │    │ URLs via LLM     │             │
│          │              │    └────────┬─────────┘             │
│          │              │             │                       │
│          │              │             ▼                       │
│          │              │    ┌──────────────────┐             │
│          │              │    │ Retrieve Full    │             │
│          │              │    │ Reddit Posts     │             │
│          │              │    └────────┬─────────┘             │
│          │              │             │                       │
│  ┌───────┼──────────────┼─────────────┼──────────┐           │
│  │       ▼              ▼             ▼          │           │
│  │  PARALLEL ANALYSIS (GPT-4o per source)        │           │
│  │                                               │           │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────┐  │           │
│  │  │  Google   │  │   Bing   │  │  Reddit    │  │           │
│  │  │ Analysis  │  │ Analysis │  │ Analysis   │  │           │
│  │  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │           │
│  │       │              │              │         │           │
│  └───────┼──────────────┼──────────────┼─────────┘           │
│          │              │              │                      │
│          └──────────────┼──────────────┘                      │
│                         │                                    │
│                         ▼                                    │
│              ┌──────────────────┐                             │
│              │   SYNTHESIS      │                             │
│              │  Combine all     │                             │
│              │  analyses into   │                             │
│              │  coherent answer │                             │
│              └────────┬─────────┘                             │
│                       │                                      │
│                       ▼                                      │
│              Final Research Report                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Interaction

```
main.py (LangGraph State Machine - 9 Nodes)
    │
    ├──→ web_operations.py
    │       ├── serp_search()      → Google/Bing SERP
    │       ├── reddit_search()    → Reddit discovery
    │       └── reddit_retrieval() → Full post content
    │
    ├──→ snapshot_operations.py
    │       ├── poll_snapshot()    → Wait for results
    │       └── download_data()   → Get JSON response
    │
    └──→ prompts.py
            ├── Reddit URL filter prompt
            ├── Google analysis prompt
            ├── Bing analysis prompt
            ├── Reddit analysis prompt
            └── Synthesis prompt
```

