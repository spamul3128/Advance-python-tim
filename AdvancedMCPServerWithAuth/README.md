# Advanced MCP Server With Auth

A **Model Context Protocol (MCP) server** with **OAuth authentication** (via Stytch), user-scoped note management, and a React frontend client.

---

## 📋 Features

- 🔐 **OAuth Authentication** — Stytch-based user auth with JWT token validation
- 📝 **Note Management** — Create, read, and list notes per authenticated user
- 🗄️ **SQLite Storage** — Lightweight persistent storage with SQLAlchemy
- 🌐 **React Frontend** — Client UI for interacting with the MCP server
- 🔒 **User Scoping** — Notes are isolated per authenticated user

---

## 🏗️ Architecture

```
┌──────────────┐     OAuth      ┌──────────────────┐     MCP      ┌──────────────┐
│   React      │ ──────────────→│  FastMCP Server   │ ──────────→ │   SQLite     │
│   Frontend   │     JWT Token  │  (backend/main.py)│   CRUD      │   Database   │
└──────────────┘                └──────────────────┘              └──────────────┘
                                       │
                                  Stytch OAuth
                                  Verification
```

---

## 📁 File Structure

```
AdvancedMCPServerWithAuth/
├── backend/
│   ├── main.py          # FastMCP server with auth and note tools
│   ├── database.py      # NoteRepository with SQLAlchemy + SQLite
│   └── pyproject.toml   # Backend dependencies
└── frontend/
    ├── src/             # React app source
    └── package.json     # Frontend dependencies
```

### Key Backend Files
| File | Purpose |
|------|---------|
| `backend/main.py` | FastMCP server definition, OAuth middleware, MCP tool endpoints |
| `backend/database.py` | `NoteRepository` class — SQLAlchemy models, CRUD operations |

### MCP Tools
| Tool | Description |
|------|-------------|
| `add_note(content)` | Create a new note for the authenticated user |
| `read_notes()` | List all notes for the authenticated user |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Stytch account (for OAuth)

### Backend Setup
```bash
cd backend
uv sync
```

Create `.env`:
```env
STYTCH_PROJECT_ID=...
STYTCH_SECRET=...
```

```bash
uv run python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📖 Logic Flow

1. **Authentication** — User authenticates via Stytch OAuth
2. **JWT Validation** — Backend validates JWT token on each request
3. **User Scoping** — User ID extracted from token scopes all operations
4. **Tool Execution** — MCP client calls `add_note` or `read_notes`
5. **Database** — SQLAlchemy persists notes to SQLite with user association
6. **Response** — Results returned via MCP protocol

---

## 📦 Dependencies

**Backend:** `fastmcp`, `python-jose`, `sqlalchemy`, `stytch`, `python-dotenv`
**Frontend:** React, TypeScript (see `frontend/package.json`)

---

## 📝 License
Educational project — use freely for learning and reference.

