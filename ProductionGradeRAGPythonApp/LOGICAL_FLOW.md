# Production Grade RAG Python App — Logical Flow

## 📋 Project Overview
A production-ready RAG application combining Inngest for event-driven workflows, Qdrant for vector storage, and OpenAI for embeddings and LLM generation.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│           Production Grade RAG Application                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ══════ INGESTION PIPELINE ══════                            │
│                                                              │
│  PDF Document                                                │
│       │                                                      │
│       ▼                                                      │
│  Inngest Event: "ingest"                                     │
│  (Throttled: 2/min, Rate limit: 1/4hr)                       │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  data_loader.py                       │                   │
│  │                                       │                   │
│  │  Step 1: Load PDF                     │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Step 2: Chunk into segments          │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Step 3: OpenAI Embedding             │                   │
│  │       (text-embedding model)          │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  vector_db.py                         │                   │
│  │                                       │                   │
│  │  Qdrant Upsert                        │                   │
│  │  ├── Vector embeddings                │                   │
│  │  ├── Payload (chunk text)             │                   │
│  │  └── Collection management            │                   │
│  └──────────────────────────────────────┘                    │
│                                                              │
│  ══════ QUERY PIPELINE ══════                                │
│                                                              │
│  User Question                                               │
│       │                                                      │
│       ▼                                                      │
│  Inngest Event: "query"                                      │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 1: Embed Question               │                   │
│  │  └── OpenAI text-embedding            │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 2: Semantic Search              │                   │
│  │  └── Qdrant vector similarity         │                   │
│  │      └── Return top-k chunks          │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 3: Generate Answer              │                   │
│  │  ├── Context: retrieved chunks        │                   │
│  │  ├── Question: user query             │                   │
│  │  └── OpenAI GPT completion            │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  Return Context-Aware Answer                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Production Features

```
Inngest Workflow Engine:
├── Throttling (2 events/min)
├── Rate Limiting (1 per 4 hours)
├── Automatic retries
└── Event-driven architecture
```

