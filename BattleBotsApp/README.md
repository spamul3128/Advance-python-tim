# BattleBots App

An **AI-powered BattleBots fight predictor** with web scraping, RAG (Retrieval-Augmented Generation), and LLM-based fight analysis — full-stack architecture with FastAPI backend and React frontend.

---

## 📋 Features

- 🤖 **Bot Scraping** — Collect bot profiles from BattleBots data + Fandom wiki
- 🧠 **RAG Pipeline** — Embed bot data for context-rich predictions
- ⚔️ **Fight Predictions** — LLM-powered outcome predictions with reasoning
- 🌐 **Full-Stack** — FastAPI backend + React/TypeScript frontend
- 🗄️ **SQLite** — Local database for bot profiles and fight history

---

## 🏗️ Architecture

```
React Frontend ◄──── API ────► FastAPI Backend
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
               Scrapers        RAG Engine        SQLite DB
              (Bright Data     (Embeddings       (Bot profiles,
               + Fandom)        + LLM)           fight history)
```

---

## 📁 File Structure
```
BattleBotsApp/
├── backend/
│   ├── main.py              # FastAPI app with CORS, routers, lifespan
│   ├── scrapers/scrape_bots.py  # Bright Data + Fandom wiki scraper
│   ├── rag/                 # RAG embedding and retrieval
│   └── routes/              # API route handlers
├── frontend/
│   ├── src/                 # React TypeScript app
│   └── package.json
└── pyproject.toml
```

---

## 🚀 Getting Started

```bash
# Backend
cd backend && uv sync && uv run python main.py

# Frontend
cd frontend && npm install && npm run dev
```

---

## 📖 Logic Flow

1. **Scrape** — Bot profiles collected from web sources
2. **Store** — Bot data persisted to SQLite
3. **Embed** — Profiles embedded into vector store
4. **Select** — User picks two bots for fight prediction
5. **Retrieve** — Relevant context from vector store
6. **Predict** — LLM analyzes bots and predicts outcome
7. **Display** — Prediction shown in frontend

---

## 📦 Dependencies
**Backend:** FastAPI, OpenAI, Anthropic, BeautifulSoup4, SQLAlchemy
**Frontend:** React, TypeScript, Vite

---

## 📝 License
Educational project — use freely for learning and reference.
