# Streamlit Intro App — Logical Flow

## 📋 Project Overview
A web-based data dashboard for exploring CSV files with interactive filtering, statistics, and charting built entirely with Streamlit.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│               Streamlit Intro App                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Streamlit Web Interface                                     │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 1: File Upload                  │                   │
│  │  └── Drag & drop CSV file             │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 2: Parse with Pandas            │                   │
│  │  └── pd.read_csv(uploaded_file)       │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 3: Data Preview                 │                   │
│  │  ├── df.head() → First rows table     │                   │
│  │  └── df.describe() → Summary stats    │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 4: Interactive Filtering        │                   │
│  │                                       │                   │
│  │  Select Column ──→ Dropdown           │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Select Value ──→ Dropdown            │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  df[column == value]                  │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Display Filtered Table               │                   │
│  └──────────────┬───────────────────────���                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  Step 5: Chart Builder                │                   │
│  │                                       │                   │
│  │  Select X-axis ──→ Column picker      │                   │
│  │  Select Y-axis ──→ Column picker      │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Generate Line Chart                  │                   │
│  │  (from filtered data)                 │                   │
│  └──────────────────────────────────────┘                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

