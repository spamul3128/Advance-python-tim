# Amazon Price Competitor Analysis LLM — Logical Flow

## 📋 Project Overview
A Streamlit dashboard that scrapes Amazon products, discovers competitors, and generates AI-powered competitive analysis reports using LangChain with GPT-4.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│          Amazon Competitor Analysis Pipeline                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Streamlit UI                                                │
│  └── User enters Amazon ASIN                                 │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────┐                                │
│  │  PRODUCT SCRAPING        │                                │
│  │  Oxylabs API             │                                │
│  │  ├── Fetch product page  │                                │
│  │  ├── Extract title       │                                │
│  │  ├── Extract price       │                                │
│  │  ├── Extract rating      │                                │
│  │  └── Extract category    │                                │
│  └────────────┬─────────────┘                                │
│               │                                              │
│               ▼                                              │
│  Display Product Card                                        │
│               │                                              │
│               ▼                                              │
│  ┌──────────────────────────────────────────┐                │
│  │  COMPETITOR DISCOVERY                     │               │
│  │  Oxylabs API (Multiple Strategies)        │               │
│  │                                           │               │
│  │  ┌───────────┐  ┌──────────┐  ┌────────┐ │               │
│  │  │ Keyword   │  │ Category │  │ Price  │ │               │
│  │  │ Search    │  │ Browse   │  │ Sort   │ │               │
│  │  └─────┬─────┘  └────┬─────┘  └───┬────┘ │               │
│  │        │              │            │      │               │
│  │        └──────────────┼────────────┘      │               │
│  │                       │                   │               │
│  └───────────────────────┼───────────────────┘               │
│                          │                                   │
│                          ▼                                   │
│  Competitor Products List (with pagination)                  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────┐                │
│  │  AI ANALYSIS (LangChain + GPT-4)         │               │
│  │                                           │               │
│  │  Input:                                   │               │
│  │  ├── Original product data                │               │
│  │  └── Competitor product data              │               │
│  │                                           │               │
│  │  Processing:                              │               │
│  │  ├── Structured prompt template           │               │
│  │  └── Pydantic output parser              │               │
│  │                                           │               │
│  │  Output (Pydantic Model):                 │               │
│  │  ├── Price comparison                     │               │
│  │  ├── Feature analysis                     │               │
│  │  ├── Market positioning                   │               │
│  │  └── Recommendations                      │               │
│  └───────────────────────┬───────────────────┘               │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────┐                │
│  │  PERSIST TO TinyDB                        │               │
│  │  └── JSON storage for history             │               │
│  └──────────────────────────────────────────┘                │
│                          │                                   │
│                          ▼                                   │
│  Display Analysis Report in Streamlit                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

