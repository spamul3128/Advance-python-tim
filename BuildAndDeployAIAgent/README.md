# Build And Deploy AI Agent

A **note-taking AI agent** built with **LangGraph** and exposed via a **FastAPI** web interface with HTML templates — demonstrates building and deploying a functional AI agent.

---

## 📋 Features

- 🤖 **ReAct Agent** — LangGraph-based reasoning + acting agent
- 📝 **File I/O Tools** — Read and write notes through natural language
- 🌐 **Web Interface** — FastAPI + Jinja2 HTML templates
- ⚡ **GPT-4o-mini** — Powered by OpenAI's efficient model

---

## 🏗️ Architecture

```
┌──────────────┐     HTTP      ┌──────────────┐    Tools     ┌──────────┐
│   Browser    │ ────────────→ │   FastAPI     │ ──────────→ │  File    │
│   (HTML UI)  │               │   + Agent     │              │  System  │
└──────────────┘               └──────┬───────┘              └──────────┘
                                      │
                               ┌──────▼───────┐
                               │  LangGraph   │
                               │  ReAct Agent │
                               │  (GPT-4o)    │
                               └──────────────┘
```

---

## 📁 File Structure

```
BuildAndDeployAIAgent/
├── main.py              # FastAPI server with routes and Jinja2 templates
├── agent.py             # LangGraph ReAct agent with read/write tools
├── requirements.txt     # Dependencies
├── note.txt             # Persistent note storage
├── templates/           # HTML templates for web UI
└── public/              # Static assets (CSS, JS)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- OpenAI API key

### Installation
```bash
cd BuildAndDeployAIAgent
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file:
```env
OPENAI_API_KEY=sk-...
```

### Run
```bash
python main.py
```
Visit `http://localhost:8000` in your browser.

---

## 📖 Logic Flow

1. **User Input** — User types a natural language request in the web UI
2. **API Route** — FastAPI receives the request as an `AgentRequest`
3. **Agent Processing** — LangGraph ReAct agent interprets the request
4. **Tool Selection** — Agent decides which tool to use:
   - `write_note(note)` → Write content to `note.txt`
   - `read_note()` → Read current content of `note.txt`
5. **Tool Execution** — Selected tool performs file I/O
6. **Response** — Agent formulates response based on tool output
7. **Display** — Response rendered in the HTML UI

### Key Components
| Component | File | Purpose |
|-----------|------|---------|
| `AgentRequest` | `main.py` | Pydantic model for incoming requests |
| `AgentResponse` | `main.py` | Pydantic model for responses |
| `write_note()` | `agent.py` | Tool to write notes to file |
| `read_note()` | `agent.py` | Tool to read notes from file |
| `create_react_agent()` | `agent.py` | LangGraph agent factory |

---

## 📦 Dependencies
```
fastapi
uvicorn
jinja2
langchain
langchain-openai
langgraph
python-dotenv
```

---

## 📝 License
Educational project — use freely for learning and reference.

