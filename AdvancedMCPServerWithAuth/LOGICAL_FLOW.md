# Advanced MCP Server With Auth — Logical Flow

## 📋 Project Overview
An OAuth-authenticated Model Context Protocol (MCP) server providing secure, user-scoped note management using FastMCP, Stytch OAuth, and SQLAlchemy ORM.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│            MCP Server Authentication Flow                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  MCP Client (e.g., Claude Desktop)                           │
│       │                                                      │
│       ▼                                                      │
│  OAuth Authentication Request                                │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────┐                                │
│  │   Stytch OAuth Provider  │                                │
│  │   ├── User login         │                                │
│  │   ├── JWT token issued   │                                │
│  │   └── JWKS validation    │                                │
│  └────────────┬─────────────┘                                │
│               │                                              │
│               ▼                                              │
│  JWT Token Validated                                         │
│       │                                                      │
│       ▼                                                      │
│  Extract User ID from Token                                  │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────────┐                │
│  │         FastMCP Server                    │               │
│  │                                           │               │
│  │    ┌─────────────┐  ┌─────────────────┐   │               │
│  │    │  add_note()  │  │ get_my_notes()  │   │               │
│  │    │  (Tool)      │  │  (Tool)         │   │               │
│  │    └──────┬──────┘  └───────┬─────────┘   │               │
│  │           │                 │              │               │
│  │           ▼                 ▼              │               │
│  │    ┌─────────────────────────────────┐     │               │
│  │    │      NoteRepository             │     │               │
│  │    │  ├── create(user_id, content)   │     │               │
│  │    │  └── get_all(user_id)           │     │               │
│  │    └──────────────┬──────────────────┘     │               │
│  │                   │                        │               │
│  │                   ▼                        │               │
│  │    ┌─────────────────────────────────┐     │               │
│  │    │     SQLite Database              │     │               │
│  │    │  ├── notes table                │     │               │
│  │    │  └── user_id scoped queries     │     │               │
│  │    └─────────────────────────────────┘     │               │
│  │                                           │               │
│  └───────────────────────────────────────────┘               │
│               │                                              │
│               ▼                                              │
│  Response returned to MCP Client                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔑 Security Flow

```
Client Request
    │
    ▼
Bearer Token in Header
    │
    ▼
Validate JWT via Stytch JWKS ──→ Invalid? → 401 Unauthorized
    │
    ▼ (Valid)
Extract user_id from claims
    │
    ▼
Scope ALL DB operations to user_id
    │
    ▼
User can only access their own notes
```

