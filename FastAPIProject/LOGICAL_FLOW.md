# FastAPI Project (Library API) — Logical Flow

## 📋 Project Overview
A RESTful library management API using FastAPI with Repository pattern, SQLite persistence, and Pydantic validation.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Library Management API                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  App Startup (Lifespan)                                      │
│       │                                                      │
│       ▼                                                      │
│  Initialize SQLite Database                                  │
│  └── Create tables if not exist                              │
│                                                              │
│  ══════ REQUEST FLOW ══════                                  │
│                                                              │
│  HTTP Request                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  FastAPI Router (books.py)            │                   │
│  │                                       │                   │
│  │  GET    /books      → List all books  │                   │
│  │  GET    /books/{id} → Get one book    │                   │
│  │  POST   /books      → Create book     │                   │
│  │  PUT    /books/{id} → Update book     │                   │
│  │  DELETE /books/{id} → Delete book     │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Pydantic Schema Validation           │                   │
│  │  ├── BookCreate (title, author, year) │                   │
│  │  └── BookResponse (+ id)              │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Repository Layer (repository.py)     │                   │
│  │  ├── get_all()                        │                   │
│  │  ├── get_by_id()                      │                   │
│  │  ├── create()                         │                   │
│  │  ├── update()                         │                   │
│  │  └── delete()                         │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  SQLite Database (library.db)         │                   │
│  │  └── books table                      │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  JSON Response                                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Pattern

```
Routes (HTTP) → Schemas (Validation) → Repository (Logic) → Database (Storage)
```

