# Inngest RAG App Demo — Logical Flow

## 📋 Project Overview
A production-grade RAG system for PDF question-answering using Inngest serverless workflows, Qdrant vector database, and OpenAI.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│                 Inngest RAG App Demo                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ══════ INGESTION PIPELINE ══════                            │
│                                                              │
│  PDF Document Upload                                         │
│       │                                                      │
│       ▼                                                      │
│  Inngest Event Trigger                                       │
│  (Rate limited: throttled execution)                         │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  data_loader.py                       │                   │
│  │                                       │                   │
│  │  1. Load PDF (LlamaIndex)             │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  2. Chunk into segments               │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  3. Generate Embeddings               │                   │
│  │     (OpenAI text-embedding)           │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Qdrant Vector Database               │                   │
│  │  └── Upsert embedded chunks           │                   │
│  └──────────────────────────────────────┘                    │
│                                                              │
│  ══════ QUERY PIPELINE ══════                                │
│                                                              │
│  Streamlit UI                                                │
│  └── User enters question                                   │
│       │                                                      │
│       ▼                                                      │
│  Inngest Event Trigger                                       │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 1: Embed Question               │                   │
│  │  └── OpenAI embedding                 │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 2: Vector Search                │                   │
│  │  └── Qdrant semantic similarity       │                   │
│  │      └── Return top-k chunks          │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 3: LLM Generation              │                   │
│  │  ├── Question + retrieved context     │                   │
│  │  ├── OpenAI GPT completion            │                   │
│  │  └── Context-aware answer             │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  Display Answer in Streamlit                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

