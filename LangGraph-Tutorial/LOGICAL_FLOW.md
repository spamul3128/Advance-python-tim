# LangGraph Tutorial — Logical Flow

## 📋 Project Overview
A dual-agent message router using LangGraph that classifies messages as emotional or logical and routes them to specialized response agents.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│              LangGraph Message Router                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  User Message Input                                          │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  NODE 1: classify_message()           │                   │
│  │                                       │                   │
│  │  Model: Claude 3.5 Sonnet             │                   │
│  │  Output: MessageClassifier            │                   │
│  │          (Pydantic structured)        │                   │
│  │                                       │                   │
│  │  Classification:                      │                   │
│  │  ├── "emotional"                      │                   │
│  │  └── "logical"                        │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  NODE 2: router()                     │                   │
│  │  (Conditional Edge)                   │                   │
│  │                                       │                   │
│  │  Evaluate message_type                │                   │
│  └──────────┬────────────┬──────────────┘                    │
│             │            │                                   │
│    "emotional"      "logical"                                │
│             │            │                                   │
│             ▼            ▼                                   │
│  ┌─────────────┐  ┌──────────────┐                           │
│  │ NODE 3a:    │  │ NODE 3b:     │                           │
│  │ therapist   │  │ logical      │                           │
│  │ _agent()    │  │ _agent()     │                           │
│  │             │  │              │                           │
│  │ Empathetic  │  │ Factual      │                           │
│  │ Supportive  │  │ Direct       │                           │
│  │ Response    │  │ Response     │                           │
│  └──────┬──────┘  └──────┬───────┘                           │
│         │                │                                   │
│         └────────┬───────┘                                   │
│                  │                                           │
│                  ▼                                            │
│  Context-Aware Response                                      │
│                  │                                           │
│                  ▼                                            │
│  Display to User ──→ Loop for next message                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧩 LangGraph State Machine

```
                    START
                      │
                      ▼
              classify_message
                      │
                      ▼
                   router
                  /       \
                 /         \
    therapist_agent    logical_agent
                 \         /
                  \       /
                    END
```

