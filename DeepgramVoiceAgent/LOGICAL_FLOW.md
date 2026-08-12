# Deepgram Voice Agent — Logical Flow

## 📋 Project Overview
A real-time voice-based pharmacy assistant using Twilio for phone calls, Deepgram for speech AI, and custom pharmacy functions for drug lookup, orders, and status checks.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│               Deepgram Voice Agent Pipeline                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Incoming Phone Call                                         │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────┐                                        │
│  │   Twilio          │                                       │
│  │   ├── Accept call │                                       │
│  │   └── WebSocket   │                                       │
│  └────────┬─────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────��───────────────────┐                    │
│  │   WebSocket Bridge (main.py)          │                   │
│  │                                       │                   │
│  │   Twilio ◄──── Audio ────► Deepgram   │                   │
│  │    WS          Chunks         WS      │                   │
│  └──────────────────┬───────────────────┘                    │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────┐                    │
│  │   Deepgram Conversational AI          │                   │
│  │                                       │                   │
│  │   1. STT (Speech-to-Text)             │                   │
│  │      Audio ──→ Transcribed Text       │                   │
│  │          │                            │                   │
│  │          ▼                            │                   │
│  │   2. LLM Reasoning                    │                   │
│  │      ├── Understand intent            │                   │
│  │      └── Decide action                │                   │
│  │          │                            │                   │
│  │     ┌────┴────────────┐               │                   │
│  │     │ Function Call?  │               │                   │
│  │     └────┬────────────┘               │                   │
│  │    Yes   │         No                 │                   │
│  │     │    │          │                 │                   │
│  │     ▼    │          ▼                 │                   │
│  │  Execute │    Direct Response         │                   │
│  │  Function│          │                 │                   │
│  │     │    │          │                 │                   │
│  └─────┼────┼──────────┼────────────────┘                    │
│        │    │          │                                     │
│        ▼    │          │                                     │
│  ┌─────────────────┐   │                                     │
│  │ Pharmacy Funcs  │   │                                     │
│  │                 │   │                                     │
│  │ get_drug_info() │   │                                     │
│  │ ├── Drug name   │   │                                     │
│  │ ├── Dosage      │   │                                     │
│  │ └── Side effects│   │                                     │
│  │                 │   │                                     │
│  │ place_order()   │   │                                     │
│  │ └── Order ID    │   │                                     │
│  │                 │   │                                     │
│  │ lookup_order()  │   │                                     │
│  │ └── Status      │   │                                     │
│  └────────┬────────┘   │                                     │
��           │            │                                     │
│           └──────┬─────┘                                     │
│                  │                                           │
│                  ▼                                            │
│   3. TTS (Text-to-Speech)                                    │
│      Response Text ──→ Audio                                 │
│                  │                                           │
│                  ▼                                            │
│   Audio streamed back via Twilio                             │
│                  │                                           │
│                  ▼                                            │
│   Caller hears response                                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

