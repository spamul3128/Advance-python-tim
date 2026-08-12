# Local AI Agent With RAG — Logical Flow

## 📋 Project Overview
A fully local RAG system using Ollama with Llama 3.2 for inference and Chroma vector database for retrieval of pizza restaurant reviews — no cloud APIs required.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│              Local AI Agent With RAG                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ══════ SETUP (One-time) ══════                              │
│                                                              │
│  CSV Reviews File                                            │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  vector.py                            │                   │
│  │                                       │                   │
│  │  1. Load CSV data                     │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  2. Generate Embeddings               │                   │
│  │     Model: mxbai-embed-large          │                   │
│  │     (Local via Ollama)                │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  3. Store in Chroma DB                │                   │
│  │     (Persistent local storage)        │                   │
│  └──────────────────────────────────────┘                    │
│                                                              │
│  ══════ QUERY FLOW ══════                                    │
│                                                              │
│  User Question (CLI)                                         │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 1: Vector Retrieval             │                   │
│  │                                       │                   │
│  │  Embed question                       │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Chroma DB similarity search          │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Return 5 most relevant reviews       │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 2: Prompt Construction          │                   │
│  │                                       │                   │
│  │  ChatPromptTemplate:                  │                   │
│  │  "You are a pizza restaurant expert"  │                   │
│  │  + Retrieved reviews as context       │                   │
│  │  + User question                      │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 3: Local LLM Inference          │                   │
│  │                                       │                   │
│  │  Model: Llama 3.2 (via Ollama)        │                   │
│  │  100% Local — No API calls            │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  Context-Aware Answer                                        │
│  (Based on actual reviews)                                   │
│                 │                                            │
│                 ▼                                            │
│  Display → Loop for next question                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
All Local — No Cloud Dependencies

Ollama (mxbai-embed-large) → Embeddings
Chroma DB                  → Vector Storage
Ollama (Llama 3.2)         → LLM Inference
```

