# FastAPI Photo/Video Sharing

A **social media platform** for photo and video sharing, built with **FastAPI** backend, **Streamlit** frontend, and **ImageKit CDN** for media storage.

---

## 📋 Features

- 📸 **Media Upload** — Photo and video upload with CDN storage
- 👤 **User Auth** — Registration and login via fastapi-users
- 📰 **Social Feed** — Browse uploaded media from all users
- 🗄️ **Async Database** — SQLAlchemy async with UUID primary keys
- 🌐 **Streamlit UI** — Clean web interface for interaction

---

## 🏗️ Architecture

```
Streamlit Frontend → FastAPI Backend → SQLAlchemy (async) → Database
                          │
                     ImageKit SDK → CDN (media storage)
```

---

## 📁 File Structure

```
FastAPIPhotoVideoSharing/
├── main.py              # Uvicorn runner
├── frontend.py          # Streamlit UI (login, upload, feed)
├── app/
│   ├── app.py           # FastAPI routes (auth, upload)
│   └── db.py            # SQLAlchemy async models (User, Post)
├── pyproject.toml
└── uv.lock
```

---

## 🚀 Getting Started

```bash
cd FastAPIPhotoVideoSharing
uv sync

# Start backend
uv run python main.py

# Start frontend (separate terminal)
uv run streamlit run frontend.py
```

### Environment Variables (.env)
```env
IMAGEKIT_PRIVATE_KEY=...
IMAGEKIT_PUBLIC_KEY=...
IMAGEKIT_URL_ENDPOINT=...
DATABASE_URL=sqlite+aiosqlite:///./app.db
```

---

## 📖 Logic Flow

1. **Register/Login** — User authenticates via Streamlit UI
2. **Upload** — User selects photo/video file
3. **CDN Storage** — File uploaded to ImageKit, URL returned
4. **Post Creation** — Post record created with CDN URL and user association
5. **Feed** — All posts displayed in reverse-chronological order

### Key Models
| Model | Purpose |
|-------|---------|
| `User` | UUID PK, auth via fastapi-users |
| `Post` | Media URL, user FK, timestamps |

---

## 📦 Dependencies
`FastAPI`, `fastapi-users`, `imagekitio`, `Streamlit`, `SQLAlchemy[asyncio]`, `uvicorn`

---

## 📝 License
Educational project — use freely for learning and reference.
