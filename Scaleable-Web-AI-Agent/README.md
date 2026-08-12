# Scaleable Web AI Agent

A **scalable newsletter generation agent** built with **FastAPI** and **Inngest** for async workflow orchestration, using **Bright Data** for web research.

---

## 📋 Features

- 📰 **Newsletter Generation** — AI-powered newsletter creation from web research
- 🔍 **SERP Search** — Bright Data integration for search engine results
- 🌐 **Web Scraping** — Async content extraction from search results
- ⏱️ **Inngest Workflows** — Serverless, scalable function orchestration
- 🧠 **LangChain** — LLM-powered content synthesis

---

## 🏗️ Architecture

```
POST /api/newsletter → Inngest Event → Research Step → Scrape Step → Generate Step → Newsletter
                                            │              │              │
                                       BrightData      Async HTTP     LangChain
                                       SERP Search     Scraping       + OpenAI
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `main.py` | FastAPI + Inngest workflow (80 lines) |
| `newsletter_service.py` | SERP search and async web scraping |
| `custom_types.py` | `NewsletterRequest` Pydantic model |

---

## 🚀 Getting Started

```bash
cd Scaleable-Web-AI-Agent
uv sync
uv run python main.py
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
BRIGHT_DATA_API_KEY=...
```

---

## 📖 Logic Flow

1. **Request** — Client sends newsletter topic via API
2. **SERP Search** — Bright Data fetches search results for the topic
3. **Web Scraping** — Top results scraped for content
4. **Synthesis** — LangChain + OpenAI generates newsletter from scraped content
5. **Response** — Generated newsletter returned

---

## 📦 Dependencies
`FastAPI`, `Inngest`, `langchain-brightdata`, `langchain`, `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.
