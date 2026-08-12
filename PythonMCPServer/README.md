# Python MCP Server

A **Model Context Protocol (MCP) server** for managing sticky notes — provides tools and prompts for note creation, reading, and summarization.

---

## 📋 Features

- 📝 **Sticky Notes** — Add, read, and retrieve latest notes via MCP tools
- 📊 **Summarization Prompt** — Built-in MCP prompt for summarizing all notes
- 🔌 **MCP Compatible** — Works with any MCP client (Claude Desktop, etc.)
- 🪶 **Lightweight** — Minimal deps, in-memory storage

---

## 🏗️ Architecture

```
MCP Client (e.g., Claude Desktop)
       │  MCP Protocol
       ▼
┌──────────────────┐
│  FastMCP Server  │
├──────────────────┤
│  Tools:          │
│  - add_note      │
│  - read_notes    │
│  - get_latest    │
├──────────────────┤
│  Prompts:        │
│  - summarize     │
└──────────────────┘
```

---

## 🚀 Getting Started

```bash
cd PythonMCPServer
uv sync
uv run python main.py
```

---

## 📖 MCP Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_note` | `content: str` | Add a new sticky note |
| `read_notes` | — | Read all stored notes |
| `get_latest_note` | — | Get the most recent note |

---

## 📖 Logic Flow

1. Server starts and registers tools + prompts
2. MCP client discovers available tools
3. Client invokes tools to manage notes
4. Summarize prompt generates overview of all notes

---

## 📦 Dependencies
`mcp[cli]`

---

## 📝 License
Educational project — use freely for learning and reference.
