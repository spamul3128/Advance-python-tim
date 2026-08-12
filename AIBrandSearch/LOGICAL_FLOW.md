# AIBrandSearch — Logical Flow

## 📋 Project Overview
A Streamlit dashboard that queries multiple LLM providers, tracks keyword mentions for brand monitoring, compares against Google SERP, and generates AI-powered meta-analysis.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    AIBrandSearch Pipeline                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Streamlit Sidebar Configuration                                 │
│  ├── Enter search prompt                                         │
│  ├── Select LLM providers (ChatGPT, Perplexity, Gemini, etc.)  │
│  ├── Define tracking keywords                                    │
│  └── Choose country                                              │
│       │                                                          │
│       ▼                                                          │
│  Click "Run Across All Models"                                   │
│       │                                                          │
│       ▼                                                          │
│  ┌────────────── PARALLEL QUERIES ──────────────┐                │
│  │                                               │               │
│  │  ┌────────┐ ┌──────────┐ ┌──────┐ ┌───────┐  │               │
│  │  │ChatGPT │ │Perplexity│ │Gemini│ │ Grok  │  │               │
│  │  └───┬────┘ └────┬─────┘ └──┬───┘ └───┬───┘  │               │
│  │      │           │          │         │      │               │
│  │      ▼           ▼          ▼         ▼      │               │
│  │       Bright Data API (Async)                 │               │
│  │       ├── Trigger query                       │               │
│  │       ├── Poll with exponential backoff       │               │
│  │       └── 5-min timeout                       │               │
│  │                                               │               │
│  └───────────────────┬───────────────────────────┘               │
│                      │                                           │
│                      ▼                                           │
│  Normalize to LLMResult Objects                                  │
│  (model_name, answer_text, status, timestamp)                    │
│                      │                                           │
│                      ▼                                           │
│  ┌──────────────────────────────────────┐                        │
│  │         KEYWORD PARSING              │                        │
│  │  ├── Regex extraction of keywords    │                        │
│  │  ├── Detect list positions (1., 2.)  │                        │
│  │  └── Generate ParsedSignals          │                        │
│  └──────────────────┬───────────────────┘                        │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────┐                        │
│  │        DISPLAY RESULTS               │                        │
│  │  ├── Signals Table (keyword matrix)  │                        │
│  │  ├── Response Tabs (highlighted)     │                        │
│  │  └── Per-model detail views          │                        │
│  └──────────────────┬───────────────────┘                        │
│                     │                                            │
│            ┌────────┴────────┐                                   │
│            ▼                 ▼                                   │
│   ┌──────────────┐  ┌────────────────────┐                       │
│   │ Fetch SERP   │  │ Run Comparative    │                       │
│   │ (Google)     │  │ Analysis (GPT-4)   │                       │
│   │ via BrightData│ │ SERP + All LLM     │                       │
│   └──────┬───────┘  │ outputs analyzed   │                       │
│          │          └────────┬───────────┘                       │
│          │                   │                                   │
│          └───────┬───────────┘                                   │
│                  ▼                                               │
│  ┌──────────────────────────────────────┐                        │
│  │     SAVE RUN DATA                    │                        │
│  │  runs/<timestamp>/                   │                        │
│  │  ├── metadata.json                   │                        │
│  │  ├── results_per_model/              │                        │
│  │  ├── signals.json                    │                        │
│  │  ├── serp.json                       │                        │
│  │  └── analysis.md                     │                        │
│  └──────────────────────────────────────┘                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

