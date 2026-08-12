# Django YouTube Clone — Logical Flow

## 📋 Project Overview
A YouTube-style video sharing platform with CDN-based video/thumbnail storage, real-time streaming, and a like/dislike voting system.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│                Django YouTube Clone                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ══════ VIDEO UPLOAD FLOW ══════                             │
│                                                              │
│  User fills Upload Form                                      │
│  (title, description, video file, thumbnail)                 │
│       │                                                      │
│       ▼                                                      │
│  POST → video_upload view                                    │
│       │                                                      │
│       ▼                                                      │
│  Validate Form Data                                          │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  ImageKit CDN Upload                  │                   │
│  │  ├── upload_video(file)              │                   │
│  │  │   └── Returns video_url, file_id  │                   │
│  │  └── upload_thumbnail(image)         │                   │
│  │       └── Returns thumbnail_url      │                   │
│  └──────────────────┬───────────────────┘                    │
│                     │                                        │
│                     ▼                                        │
│  Create Video Model Instance                                 │
│  (title, description, file_id, URLs, views=0)                │
│                     │                                        │
│                     ▼                                        │
│  Save to Database                                            │
│                                                              │
│  ══════ VIDEO VIEWING FLOW ══════                            │
│                                                              │
│  User navigates to video list                                │
│       │                                                      │
│       ▼                                                      │
│  video_list view ──→ Display feed                            │
│       │                                                      │
│       ▼                                                      │
│  Click video ──→ video_detail view                           │
│       │                                                      │
│       ├── Increment views += 1                               │
│       ├── Get streaming URL from ImageKit                    │
│       ├── Get thumbnail with watermark                       │
│       └── Check user's existing vote                         │
│       │                                                      │
│       ▼                                                      │
│  Render Video Player                                         │
│                                                              │
│  ══════ VOTING FLOW ══════                                   │
│                                                              │
│  User clicks Like/Dislike                                    │
│       │                                                      │
│       ▼                                                      │
│  POST → video_vote view                                      │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  Check Existing Vote                  │                   │
│  │       │                               │                   │
│  │  ┌────┴────────────────┐              │                   │
│  │  │                     │              │                   │
│  │  ▼                     ▼              │                   │
│  │  No vote exists    Vote exists        │                   │
│  │  │                     │              │                   │
│  │  ▼                     ▼              │                   │
│  │  Create new        Same value?        │                   │
│  │  VideoLike         ├── Yes → Remove   │                   │
│  │  record            └── No → Flip      │                   │
│  │  │                     │              │                   │
│  │  └─────────┬───────────┘              │                   │
│  │            ▼                          │                   │
│  │  Adjust like/dislike counters         │                   │
│  │  (atomic update)                      │                   │
│  └──────────────────┬───────────────────┘                    │
│                     │                                        │
│                     ▼                                        │
│  Return JSON { likes, dislikes, user_vote }                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

