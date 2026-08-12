# Agentspan Course

A hands-on course workspace featuring **three progressively complex AI agents** built with the **Agentspan** framework — covering conversation memory, guardrails, and web research.

---

## 📋 Agents Overview

| # | Agent | File | Description |
|---|-------|------|-------------|
| 1 | **Personal Assistant** | `agents/agent1.py` | Conversational agent with time tool and memory |
| 2 | **Customer Support** | `agents/agent2.py` | Guardrailed agent with structured Pydantic responses |
| 3 | **Research Agent** | `agents/agent3.py` | Web research agent using Firecrawl for live searches |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- OpenAI API key
- Firecrawl API key (for Agent 3)

### Installation
```bash
cd Agentspan-Course
uv sync
```

### Environment Variables
Create a `.env` file:
```env
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=...
```

### Run Any Agent
```bash
uv run python agents/agent1.py
uv run python agents/agent2.py
uv run python agents/agent3.py
```

---

## 📖 Agent Details

### Agent 1 — Personal Assistant (`agents/agent1.py`)
**Capabilities:**
- Current time retrieval tool
- Conversation memory across turns
- Friendly, helpful personality

**Logic Flow:**
1. User sends a message
2. Agent checks if a tool call is needed (e.g., "What time is it?")
3. Tool result is injected into context
4. Agent responds with memory of previous messages

---

### Agent 2 — Customer Support (`agents/agent2.py`)
**Capabilities:**
- Input guardrails (blocks off-topic or harmful queries)
- Structured Pydantic response schema
- Professional support tone

**Logic Flow:**
1. User query passes through guardrail check
2. If valid → Agent processes and responds with structured output
3. If blocked → Guardrail rejection message returned

---

### Agent 3 — Research Agent (`agents/agent3.py`)
**Capabilities:**
- Live web search via Firecrawl API
- Multi-step research workflows
- Source-backed answers

**Logic Flow:**
1. User asks a research question
2. Agent uses Firecrawl to search the web
3. Results are analyzed and synthesized
4. Answer is returned with sources

---

## 📁 Project Structure
```
Agentspan-Course/
├── agents/
│   ├── agent1.py        # Personal assistant with memory
│   ├── agent2.py        # Customer support with guardrails
│   └── agent3.py        # Research agent with Firecrawl
├── reports/             # Generated research reports
├── pyproject.toml       # Dependencies
└── uv.lock
```

---

## 📦 Dependencies
- `agentspan`
- `firecrawl-py`
- `pydantic`
- `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.

