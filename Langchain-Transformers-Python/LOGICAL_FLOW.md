# LangChain Transformers Python — Logical Flow

## 📋 Project Overview
Text summarization and Q&A system using HuggingFace transformer models (BART for summarization, RoBERTa for Q&A) with LangChain integration and GPU acceleration.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│           LangChain Transformers Pipeline                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Input Text (article, document, etc.)                        │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  STAGE 1: Primary Summarization       │                   │
│  │                                       │                   │
│  │  Model: BART-large-CNN                │                   │
│  │  Device: CUDA (GPU 0)                 │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Abstractive Summary v1               │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  STAGE 2: Summary Refinement          │                   │
│  │                                       │                   │
│  │  Model: BART-large                    │                   │
│  │  Device: CUDA (GPU 0)                 │                   │
│  │       │                               │                   │
│  │       ▼                               │                   │
│  │  Refined Summary v2                   │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  Display Final Summary                                       │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  STAGE 3: Question Answering Loop     │                   │
│  │                                       │  ◄────┐           │
│  │  User asks question                   │       │           │
│  │       │                               │       │           │
│  │       ▼                               │       │           │
│  │  Model: RoBERTa-base-squad2           │       │           │
│  │  Context: Refined summary             │       │           │
│  │       │                               │       │           │
│  │       ▼                               │       │           │
│  │  Extract Answer from Context          │       │           │
│  │       │                               │       │           │
│  │       ▼                               │       │           │
│  │  Display Answer ──────────────────────┼───────┘           │
│  │                                       │                   │
│  └──────────────────────────────────────┘                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧩 Model Pipeline

```
Text ──→ BART-large-CNN ──→ BART-large ──→ RoBERTa-base-squad2
         (Summarize)        (Refine)        (Answer Questions)
```

