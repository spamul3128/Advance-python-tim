# Python AI Agent in 10 Minutes

A **data generation agent** built with **LangGraph** that creates synthetic user datasets through natural language — complete with JSON persistence and conversation history.

---

## 📋 Features

- 🧑‍🤝‍🧑 **User Data Generation** — Create synthetic user datasets with customizable fields
- 💾 **JSON Persistence** — Read and write data to JSON files
- 💬 **Conversation History** — Multi-turn interactions with memory
- 🛠️ **Tool-based Agent** — LangGraph ReAct pattern with tool decorators
- ⚡ **Quick Setup** — Minimal code, maximum capability

---

## 🏗️ Architecture

```
User Request → LangGraph ReAct Agent → Tool Selection
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
          generate_sample_users()     write_json()            read_json()
          (create synthetic data)     (save to file)          (load from file)
```

---

## 🚀 Getting Started

```bash
cd PythonAIAgentin10Minutes
uv sync
uv run python main.py
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
```

---

## 📖 Logic Flow

1. **Input** — User describes what data they need (e.g., "Generate 50 users with names and emails")
2. **Agent Reasoning** — Agent determines the best approach
3. **Data Generation** — `generate_sample_users()` creates synthetic data with customizable parameters
4. **Persistence** — `write_json()` saves data to a JSON file
5. **Verification** — `read_json()` can reload and display the data
6. **Conversation** — History maintained for follow-up requests

### Tools
| Tool | Purpose |
|------|---------|
| `generate_sample_users(count, fields)` | Create synthetic user records |
| `write_json(filename, data)` | Save data to JSON file |
| `read_json(filename)` | Load and display JSON file contents |

---

## 📦 Dependencies
`langchain`, `langchain-openai`, `langgraph`, `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.
