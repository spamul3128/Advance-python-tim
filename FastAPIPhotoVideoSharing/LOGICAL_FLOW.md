# FastAPI Photo Video Sharing — Logical Flow

## 📋 Project Overview
A social media platform for uploading photos/videos to ImageKit CDN with JWT authentication, Streamlit frontend, and async SQLAlchemy ORM.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│            FastAPI Photo Video Sharing                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ══════ AUTHENTICATION FLOW ══════                           │
│                                                              │
│  Streamlit UI                                                │
│       │                                                      │
│       ├── Register ──→ POST /auth/register                   │
│       │                  └── Create User (UUID, hashed pwd)  │
│       │                                                      │
│       └── Login ──→ POST /auth/login                         │
│                      └── Validate credentials                │
│                      └── Return JWT Token                    │
│                              │                               │
│                              ▼                               │
│                     Store token in session                    │
│                                                              │
│  ══════ UPLOAD FLOW ══════                                   │
│                                                              │
│  Select file (photo/video)                                   │
│       │                                                      │
│       ▼                                                      │
│  POST /upload (with JWT)                                     │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  1. Validate JWT Token                │                   │
│  │  2. Upload to ImageKit CDN            │                   │
│  │     └── Returns CDN URL               │                   │
│  │  3. Create Post Record                │                   │
│  │     ├── user_id (UUID)                │                   │
│  │     ├── media_url (CDN)               │                   │
│  │     └── timestamp                     │                   │
│  │  4. Save to SQLAlchemy DB             │                   │
│  └──────────────────────────────────────┘                    │
│                                                              │
│  ══════ FEED FLOW ══════                                     │
│                                                              │
│  GET /feed                                                   │
│       │                                                      │
│       ▼                                                      │
│  Query Posts (reverse chronological)                         │
│       │                                                      │
│       ▼                                                      │
│  Return Post List with CDN URLs                              │
│       │                                                      │
│       ▼                                                      │
│  Streamlit renders media grid                                │
│                                                              │
│  ══════ DELETE FLOW ══════                                   │
│                                                              │
│  DELETE /post/{id} (with JWT)                                │
│       │                                                      │
│       ▼                                                      │
│  Verify ownership → Delete from DB                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

