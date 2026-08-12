# Production Grade RAG Python App

A **production-ready RAG application** using **Inngest** for serverless workflow management and **Qdrant** for vector storage — with built-in throttling and rate limiting.

---

## 📋 Features

- 📄 **PDF Ingestion** — Automated load, chunk, embed, upsert pipeline
- 🔍 **Vector Search** — Qdrant semantic search
- 🧠 **LLM Generation** — OpenAI-powered contextual answers
- ⏱️ **Production Controls** — Throttle (2/min) and rate limit (1/4hr)
- 🔄 **Event-Driven** — Inngest serverless function orchestration

---

## 🏗️ Architecture

```
Inngest Events → FastAPI Server
                      │
            ┌─────────┼─────────┐
            ▼                   ▼
    rag_ingest_pdf        rag_query_pdf
    [Load→Chunk→Embed     [Search→Retrieve
     →Upsert Qdrant]       →LLM→Answer]
```

---

## 🚀 Getting Started

```bash
cd ProductionGradeRAGPythonApp
uv sync
uv run python main.py
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
QDRANT_URL=...
QDRANT_API_KEY=...
```

---

## 📖 Logic Flow

### Ingestion (throttled)
1. PDF loaded and text extracted
2. Text chunked into segments
3. Chunks embedded via OpenAI
4. Vectors upserted to Qdrant

### Query
1. User question embedded
2. Top-k similar chunks retrieved
3. Context assembled from chunks
4. OpenAI generates contextual answer

---

## 📦 Dependencies
`fastapi`, `inngest`, `langchain`, `qdrant-client`, `openai`, `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.
