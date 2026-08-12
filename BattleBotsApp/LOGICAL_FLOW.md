# BattleBots App — Logical Flow

## 📋 Project Overview
A full-stack AI fight predictor that scrapes bot profiles, embeds them via RAG, and uses LLM analysis with historical match context to predict fight outcomes.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│                 BattleBots Prediction Pipeline                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────┐                    │
│  │  DATA INGESTION (One-time Setup)      │                   │
│  │                                       │                   │
│  │  Bright Data Scraper ──┐              │                   │
│  │  Fandom Wiki Scraper ──┤              │                   │
│  │                        ▼              │                   │
│  │  Bot Profiles Database                │                   │
│  │  ├── Name, weapon type               │                   │
│  │  ├── Win/loss records                │                   │
│  │  └── Fight history                    │                   │
│  │           │                           │                   │
│  │           ▼                           │                   │
│  │  Vector Embeddings (RAG)              │                   │
│  └───────────────────────────────────────┘                   │
│                                                              │
│  ──────── PREDICTION REQUEST ────────                        │
│                                                              │
│  Frontend (React)                                            │
│  └── Select Bot A vs Bot B                                   │
│       │                                                      │
│       ▼                                                      │
│  POST /api/predict                                           │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  PREDICTOR ENGINE                     │                   │
│  │                                       │                   │
│  │  1. Check prediction cache            │                   │
│  │     ├── Hit ──→ Return cached result  │                   │
│  │     └── Miss ──→ Continue             │                   │
│  │          │                            │                   │
│  │          ▼                            │                   │
│  │  2. Fetch Bot Profiles                │                   │
│  │     ├── Bot A details                 │                   │
│  │     └── Bot B details                 │                   │
│  │          │                            │                   │
│  │          ▼                            │                   │
│  │  3. Enrich with History               │                   │
│  │     ├── Past match results            │                   │
│  │     └── Sentiment analysis            │                   │
│  │          │                            │                   │
│  │          ▼                            │                   │
│  │  4. RAG Context Retrieval             │                   │
│  │     └── Vector similarity search      │                   │
│  │          │                            │                   │
│  │          ▼                            │                   │
│  │  5. LLM Prediction                    │                   │
│  │     ├── Bot profiles + history        │                   │
│  │     ├── RAG context                   │                   │
│  │     └── Generate prediction           │                   │
│  │          │                            │                   │
│  │          ▼                            │                   │
│  │  6. Format Response                   │                   │
│  │     ├── Winner prediction             │                   │
│  │     ├── Confidence score              │                   │
│  │     └── Evidence citations            │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  Return Prediction to Frontend                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

