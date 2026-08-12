# Ollama Tutorial — Logical Flow

## 📋 Project Overview
Hands-on tutorial demonstrating how to interact with Ollama (local LLM runtime) using both HTTP API and Python SDK approaches.

---

## 🔄 Approach 1: HTTP API (sample_request.py)

```
┌─────────────────────────────────────────────────────┐
│              HTTP API Approach                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User Prompt                                        │
│       │                                             │
│       ▼                                             │
│  Build JSON Request                                 │
│  {                                                  │
│    "model": "model_name",                           │
│    "messages": [{"role":"user","content":"..."}]    │
│  }                                                  │
│       │                                             │
│       ▼                                             │
│  POST → localhost:11434/api/chat                    │
│  (stream=True)                                      │
│       │                                             │
│       ▼                                             │
│  ┌─────────────────────────┐                        │
│  │  Stream Response Chunks │  ◄────┐                │
│  │       │                 │       │                │
│  │       ▼                 │       │                │
│  │  Parse JSON line        │       │                │
│  │       │                 │       │                │
│  │       ▼                 │       │                │
│  │  Extract token          │       │                │
│  │       │                 │       │                │
│  │       ▼                 │       │                │
│  │  Print token ───────────┼───────┘                │
│  │  (real-time display)    │  until done=true       │
│  └─────────────────────────┘                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Approach 2: Python SDK (package.py)

```
┌─────────────────────────────────────────────────────┐
│              Python SDK Approach                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  import ollama                                      │
│       │                                             │
│       ▼                                             │
│  ollama.chat(                                       │
│    model="model_name",                              │
│    messages=[...]                                   │
│  )                                                  │
│       │                                             │
│       ▼                                             │
│  SDK handles HTTP communication                     │
│       │                                             │
│       ▼                                             │
│  Response object returned                           │
│       │                                             │
│       ▼                                             │
│  Extract message.content                            │
│       │                                             │
│       ▼                                             │
│  Display response                                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

