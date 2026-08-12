# Python AI Agent From Scratch — Logical Flow

## 📋 Project Overview
An AI research agent built with LangChain and Claude 3.5 Sonnet, providing web search, Wikipedia lookup, and file saving with structured Pydantic output.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│            Python AI Agent From Scratch                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  User Research Question                                      │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  Claude 3.5 Sonnet Agent              │                   │
│  │                                       │                   │
│  │  Prompt Template:                     │                   │
│  │  "Research the topic and provide      │                   │
│  │   a structured response"              │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Agent Reasoning                      │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Tool Selection                       │                   │
│  └──────────┬───────────────────────────┘                    │
│             │                                                │
│        ┌────┼────────────┐                                   │
│        ▼    ▼            ▼                                   │
│                                                              │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐                  │
│  │DuckDuckGo│  │ Wikipedia │  │   Save   │                  │
│  │ Search   │  │  Lookup   │  │  to File │                  │
│  │          │  │           │  │          │                  │
│  │ Web      │  │ Summary   │  │ .txt     │                  │
│  │ results  │  │ articles  │  │ output   │                  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘                  │
│       │              │             │                         │
│       └──────────────┼─────────────┘                         │
│                      │                                       │
│                      ▼                                       │
│  ┌──────────────────────────────────────┐                    │
│  │  Pydantic Output Parser              │                   │
│  │                                       │                   │
│  │  ResearchResponse:                    │                   │
│  │  ├── topic: str                       │                   │
│  │  ├── summary: str                     │                   │
│  │  ├── sources: List[str]               │                   │
│  │  ├── tools_used: List[str]            │                   │
│  │  └── confidence: float                │                   │
│  └──────────────────┬───────────────────┘                    │
│                     │                                        │
│                     ▼                                        │
│  Display Structured Research Report                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

