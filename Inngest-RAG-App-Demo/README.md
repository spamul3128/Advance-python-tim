# Inngest RAG App Demo

A production-ready **Retrieval-Augmented Generation (RAG)** application using **Inngest** for serverless event-driven workflows, **Qdrant** for vector storage, and **Streamlit** for the UI.

---

## 📋 Features

- 📄 **PDF Ingestion** — Load, chunk, embed, and store PDF documents
- 🔍 **Vector Search** — Qdrant-powered semantic search over documents
- 🧠 **LLM Generation** — OpenAI answers questions with retrieved context
- ⏱️ **Throttling** — Rate-limited workflows via Inngest
- 🌐 **Streamlit UI** — Web interface for queries

---

## 🏗️ Architecture

```
PDF Upload → Inngest Event → [Load PDF → Chunk → Embed → Upsert to Qdrant]
                                         (throttled, rate-limited)

User Query → Inngest Event → [Vector Search → Retrieve Context → OpenAI LLM → Answer]
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `main.py` | FastAPI + Inngest functions (ingest + query) |
| `data_loader.py` | PDF loading and text chunking |
| `vector_db.py` | Qdrant vector store integration |
| `custom_types.py` | Pydantic models (RAGChunksAndSrc, RAGQueryResult, etc.) |
| `streamlit_app.py` | Streamlit web UI |

---

## 🚀 Getting Started

```bash
cd Inngest-RAG-App-Demo
uv sync

# Start API server
uv run python main.py

# Start Streamlit UI (separate terminal)
uv run streamlit run streamlit_app.py
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
QDRANT_URL=...
QDRANT_API_KEY=...
```

---

## 📖 Logic Flow

### Ingestion Pipeline
1. **PDF loaded** → Text extracted page-by-page
2. **Chunking** → Text split into manageable chunks
3. **Embedding** → Chunks embedded via OpenAI embeddings
4. **Upsert** → Vectors stored in Qdrant collection

### Query Pipeline
1. **User query** → Embedded into vector
2. **Search** → Top-k similar chunks retrieved from Qdrant
3. **Context** → Retrieved chunks assembled as context
4. **LLM** → OpenAI generates answer using context
5. **Response** → Answer displayed in Streamlit

### Inngest Configuration
- **Throttle:** 2 requests per minute
- **Rate Limit:** 1 per 4 hours (for ingestion)

---

## 📦 Dependencies
`fastapi`, `inngest`, `langchain`, `qdrant-client`, `openai`, `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.
