# Python AI Agent From Scratch

Build an AI agent from fundamental principles using **LangChain** with **Claude 3.5 Sonnet**, featuring **web search**, **Wikipedia lookup**, and **file saving** tools.

---

## 📋 Features

- 🔍 **DuckDuckGo Search** — Web search for current information
- 📚 **Wikipedia** — Encyclopedia lookup for knowledge queries
- 💾 **File Saving** — Save research results to text files
- 🧠 **Claude 3.5 Sonnet** — Anthropic's powerful reasoning model
- 📐 **Structured Output** — Pydantic-validated responses

---

## 🏗️ Architecture

```
User Query → LangChain Agent → Tool Selection
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              DuckDuckGo       Wikipedia        save_to_file()
              Search           Lookup
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                          Structured Response
                          (Pydantic model)
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `main.py` | Agent setup with Claude 3.5 Sonnet and structured output |
| `tools.py` | DuckDuckGo, Wikipedia, and file save tool definitions |

---

## 🚀 Getting Started

```bash
cd PythonAIAgentFromScratch
pip install -r requirements.txt
python main.py
```

### Environment Variables (.env)
```env
ANTHROPIC_API_KEY=...
```

---

## 📖 Logic Flow

1. **Input** — User provides a research question
2. **Agent Reasoning** — Claude 3.5 Sonnet decides which tools to use
3. **Tool Execution** — Web search, Wikipedia, or file operations
4. **Structured Output** — Response validated against Pydantic schema
5. **Display** — Clean, structured answer presented

---

## 📦 Dependencies
`langchain`, `langchain-anthropic`, `duckduckgo-search`, `wikipedia`, `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.
