# Advanced Langflow Web Agent

A **multi-source research agent** built with LangGraph that searches **Google, Bing, and Reddit** in parallel, analyzes results from each source independently, and synthesizes a comprehensive final answer.

---

## 📋 Features

- 🔍 **Parallel multi-engine search** — Google, Bing, and Reddit simultaneously
- 🧠 **Per-source AI analysis** — Each source gets its own LLM analysis pass
- 🔗 **Reddit deep-dive** — Fetches and analyzes actual Reddit post content
- 📊 **Synthesis** — Merges all analyses into one cohesive answer
- ⚡ **Bright Data integration** — Uses SERP and web scraping APIs

---

## 🏗️ Architecture

```
User Query → START
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
  Google     Bing      Reddit Search
  Search     Search       │
    │          │      Reddit URL Analysis
    │          │          │
    │          │      Reddit Post Retrieval
    │          │          │
  Google     Bing      Reddit
  Analysis   Analysis  Analysis
    │          │          │
    └──────────┼──────────┘
               ▼
         Synthesize All → Final Answer
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `main.py` | LangGraph state machine with 9 nodes, parallel branching, and synthesis |
| `prompts.py` | `PromptTemplates` class — system/user prompts for each search source |
| `web_operations.py` | Bright Data API integration for SERP and Reddit searches |
| `snapshot_operations.py` | Async polling and download logic for search results |
| `pyproject.toml` | Dependencies and project metadata |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- OpenAI API key
- Bright Data API credentials

### Installation
```bash
cd Advanced-Langflow-Web-Agent
uv sync
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
BRIGHT_DATA_API_KEY=...
```

### Run
```bash
uv run python main.py
```

---

## 📖 Logic Flow

1. **Input** — User provides a research question
2. **Parallel Search** — Three concurrent API calls via Bright Data
3. **Reddit Enhancement** — Reddit URLs analyzed and full post content retrieved
4. **Individual Analysis** — Each source analyzed independently by GPT
5. **Synthesis** — All three analyses combined into one comprehensive answer

### Key Functions
| Function | File | Description |
|----------|------|-------------|
| `serp_search()` | `web_operations.py` | Triggers SERP search via Bright Data |
| `reddit_search_api()` | `web_operations.py` | Reddit-specific search |
| `reddit_post_retrieval()` | `main.py` | Fetches full Reddit post content |
| `synthesize_analyses()` | `main.py` | Merges all source analyses |

---

## 📦 Dependencies
- `langchain` >= 0.3.27 · `langchain-openai` >= 0.3.29 · `langgraph` >= 0.6.4 · `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.
