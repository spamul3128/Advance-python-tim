# API For Your LLM — Logical Flow

## 📋 Project Overview
A FastAPI REST API wrapping a local Ollama LLM (Mistral) with API key authentication and a credit-based usage tracking system.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  API For Your LLM                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Client (test-api.py)                                        │
│       │                                                      │
│       ▼                                                      │
│  POST /generate                                              │
│  Headers: { x-api-key: "user-key" }                          │
│  Body: { prompt: "..." }                                     │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────┐                            │
│  │   verify_api_key()           │                            │
│  │   (FastAPI Dependency)       │                            │
│  │                              │                            │
│  │   Extract x-api-key header   │                            │
│  │          │                   │                            │
│  │     ┌────┴────┐              │                            │
│  │     │ Valid?  │              │                            │
│  │     └────┬────┘              │                            │
│  │   No     │    Yes            │                            │
│  │   │      │                   │                            │
│  │   ▼      ▼                   │                            │
│  │  401   Check Credits         │                            │
│  │         │                    │                            │
│  │    ┌────┴────┐               │                            │
│  │    │ > 0 ?   │               │                            │
│  │    └────┬────┘               │                            │
│  │  No     │    Yes             │                            │
│  │  │      │                    │                            │
│  │  ▼      ▼                    │                            │
│  │ 401   Pass ✓                 │                            │
│  └──────────┬───────────────────┘                            │
│             │                                                │
│             ▼                                                │
│  Deduct 1 Credit                                             │
│             │                                                │
│             ▼                                                │
│  ┌──────────────────────────────┐                            │
│  │   Ollama (Local LLM)         │                            │
│  │   Model: Mistral             │                            │
│  │   ollama.chat(prompt)        │                            │
│  └──────────────┬───────────────┘                            │
│                 │                                            │
│                 ▼                                            │
│  Return JSON Response                                        │
│  { "response": "generated text" }                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔑 Credit System

```
API_KEY_CREDITS = {
    "key1": 10,    ──→  10 requests remaining
    "key2": 5,     ──→   5 requests remaining
}

Each successful request: credits -= 1
Credits == 0: 401 Unauthorized
```

