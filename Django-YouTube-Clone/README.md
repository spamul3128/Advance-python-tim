# Django YouTube Clone

A **YouTube-style video sharing platform** built with **Django** and **ImageKit CDN** for video/thumbnail storage and streaming.

---

## 📋 Features

- 📹 **Video Upload** — Upload videos with automatic CDN storage via ImageKit
- 🖼️ **Thumbnails** — Auto-generated thumbnail support
- 👍 **Like/Dislike** — Voting system for videos
- 📺 **Streaming** — Video streaming via CDN URLs
- 🔐 **User Authentication** — Django auth system

---

## 🏗️ Architecture

```
Browser → Django Views → Video/VideoLike Models → SQLite DB
                │                                      │
           ImageKit SDK ──→ ImageKit CDN (video + thumbnail storage)
```

---

## 📁 File Structure

```
Django-YouTube-Clone/
├── youtube/
│   ├── manage.py            # Django management
│   ├── youtube/             # Project settings
│   │   ├── settings.py
│   │   └── urls.py
│   └── videos/
│       ├── models.py        # Video, VideoLike models
│       ├── views.py         # CRUD, upload, like/dislike views
│       ├── urls.py          # URL routing
│       └── templates/       # HTML templates
├── pyproject.toml
└── uv.lock
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+, ImageKit account

```bash
cd Django-YouTube-Clone
uv sync
cd youtube
python manage.py migrate
python manage.py runserver
```

### Environment Variables (.env)
```env
IMAGEKIT_PRIVATE_KEY=...
IMAGEKIT_PUBLIC_KEY=...
IMAGEKIT_URL_ENDPOINT=...
```

---

## 📖 Logic Flow

1. **Upload** — User uploads video file via form
2. **CDN Storage** — Video uploaded to ImageKit CDN, URL stored in DB
3. **Model Creation** — `Video` model created with title, description, CDN URLs
4. **Streaming** — Video served via CDN streaming URL
5. **Interaction** — Users can like/dislike (one vote per user per video)
6. **Display** — Video feed with thumbnails and metadata

### Key Models
| Model | Fields | Purpose |
|-------|--------|---------|
| `Video` | title, description, video_url, thumbnail_url, created_at | Video content |
| `VideoLike` | video (FK), user (FK), is_like | Like/dislike votes |

---

## 📦 Dependencies
- `Django` >= 6.0
- `imagekitio`

---

## 📝 License
Educational project — use freely for learning and reference.
