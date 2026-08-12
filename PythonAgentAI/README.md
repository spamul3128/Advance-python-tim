# Python Agent AI

A **multi-tool ReAct agent** built with **LlamaIndex** that combines **data analysis** (Pandas), **PDF reading**, **web scraping** (Scrapeless), and **note-taking** capabilities.

---

## 📋 Features

- 📊 **Data Analysis** — Query CSV/DataFrames with natural language via Pandas
- 📄 **PDF Reader** — Extract and query information from PDF documents
- 🌐 **Web Scraping** — Google Maps location data via Scrapeless API
- 📝 **Note Engine** — Save and retrieve text notes to files
- 🧠 **GPT-4o-mini** — 128k context window for large documents

---

## 🏗️ Architecture

```
User Query → LlamaIndex ReActAgent → Tool Selection
                                          │
                    ┌─────────────────────┼────────────────────┐
                    ▼                     ▼                    ▼
            PandasQueryEngine      PDFReader Tool        Scrapeless API
            (CSV analysis)         (document QA)         (location data)
                    │                     │                    │
                    └─────────────────────┼────────────────────┘
                                          ▼
                                    note_engine
                                    (save results)
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `main.py` | ReActAgent setup with tools and interactive loop |
| `prompts.py` | Pandas query instructions and context prompts |
| `coffee_scraper.py` | Scrapeless API client for Google Maps data |
| `note_engine.py` | File-based note saving tool |

---

## 🚀 Getting Started

```bash
cd PythonAgentAI
pip install -r requirements.txt
python main.py
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
SCRAPELESS_API_KEY=...
```

---

## 📖 Logic Flow

1. **Input** — User asks a question in natural language
2. **Reasoning** — ReActAgent decides which tool(s) to use
3. **Tool Execution** — Selected tool processes the request
4. **Multi-step** — Agent may chain multiple tools
5. **Response** — Final answer synthesized from tool outputs
6. **Save** — Results can be saved via note_engine

---

## 📦 Dependencies
`llama-index`, `pandas`, `python-dotenv`, `requests`

---

## 📝 License
Educational project — use freely for learning and reference.
