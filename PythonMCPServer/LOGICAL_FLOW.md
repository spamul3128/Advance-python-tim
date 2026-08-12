# Python MCP Server — Logical Flow

## 📋 Project Overview
A Model Context Protocol (MCP) server providing sticky notes management tools and summarization prompts for integration with MCP clients like Claude Desktop.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  Python MCP Server                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  MCP Client (e.g., Claude Desktop)                           │
│       │                                                      │
│       ▼                                                      │
│  Connect to FastMCP Server                                   │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  Tool Discovery                       │                   │
│  │  Client discovers available tools:    │                   │
│  │  ├── add_note                         │                   │
│  │  ├── read_notes                       │                   │
│  │  └── get_latest_note                  │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Tool Invocation                      │                   │
│  │                                       │                   │
│  │  add_note(name, content)              │                   │
│  │  ├── Creates note with name + content │                   │
│  │  └── Returns confirmation             │                   │
│  │       │                               │                   │
│  │  read_notes()                         │                   │
│  │  ├── Returns all stored notes         │                   │
│  │  └── Formatted list                   │                   │
│  │       │                               │                   │
│  │  get_latest_note()                    │                   │
│  │  ├── Returns most recent note         │                   │
│  │  └── Name + content                   │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Prompt Resource                      │                   │
│  │                                       │                   │
│  │  note_summary_prompt:                 │                   │
│  │  ├── Retrieves all notes              │                   │
│  │  ├── Builds summary request           │                   │
│  │  └── LLM generates overview           │                   │
│  └──────────────────────────────────────┘                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧩 MCP Architecture

```
┌──────────────┐         ┌──────────────────┐
│  MCP Client  │ ◄─────► │  FastMCP Server  │
│  (Claude     │  MCP    │                  │
│   Desktop)   │ Protocol│  Tools:          │
│              │         │  ├── add_note    │
│              │         │  ├── read_notes  │
│              │         │  └── get_latest  │
│              │         │                  │
│              │         │  Prompts:        │
│              │         │  └── summary     │
└──────────────┘         └──────────────────┘
```

