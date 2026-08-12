# Scaleable Web AI Agent — Logical Flow

## 📋 Project Overview
Generates AI-powered newsletters from web research using BrightData SERP, OpenAI LLM, and Inngest for scalable event-driven workflows that handle 100+ concurrent requests.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│             Scaleable Web AI Agent                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  API Request (or Load Test: 100 concurrent)                  │
│  POST /newsletter { topic: "..." }                           │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  FastAPI Server                       │                   │
│  │  └── Trigger Inngest Event            │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Inngest Workflow Engine              │                   │
│  │  (Handles concurrency & retries)      │                   │
│  │                                       │                   │
│  │  Step 1: Web Research                 │                   │
│  │  ┌──────────────────────────────┐     │                   │
│  │  │  newsletter_service.py       │     │                   │
│  │  │                              │     │                   │
│  │  │  BrightData SERP Search      │     │                   │
│  │  │  ├── Query topic             │     │                   │
│  │  │  ├── Get search results      │     │                   │
│  │  │  └── Extract:                │     │                   │
│  │  │      ├── Titles              │     │                   │
│  │  │      ├── Descriptions        │     │                   │
│  │  │      └── Sources             │     │                   │
│  │  └──────────────┬───────────────┘     │                   │
│  │                 │                     │                   │
│  │                 ▼                     │                   │
│  │  Step 2: Content Generation           │                   │
│  │  ┌──────────────────────────────┐     │                   │
│  │  │  LangChain + GPT-4o          │     │                   │
│  │  │                              │     │                   │
│  │  │  Input: SERP results         │     │                   │
│  │  │  Output: Newsletter content  │     │                   │
│  │  │  (Structured, formatted)     │     │                   │
│  │  └──────────────┬───────────────┘     │                   │
│  │                 │                     │                   │
│  │                 ▼                     │                   │
│  │  Step 3: Save Output                  │                   │
│  │  └── Write to markdown file           │                   │
│  │                                       │                   │
│  └──────────────────────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  Return newsletter file path                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## ⚡ Scalability Architecture

```
100 Concurrent Requests
         │
         ▼
    FastAPI Server
         │
         ▼
    Inngest Queue
    ├── Event 1 ──→ Search → Generate → Save
    ├── Event 2 ──→ Search → Generate → Save
    ├── Event 3 ──→ Search → Generate → Save
    └── ... (auto-scaled, retried on failure)
```

