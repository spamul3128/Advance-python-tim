# Agentspan Course — Logical Flow

## 📋 Project Overview
Three progressively complex AI agents demonstrating Agentspan capabilities: personal assistant, customer support with guardrails, and multi-agent research orchestration.

---

## 🔄 Agent 1: Personal Assistant

```
┌─────────────────────────────────────────────────────┐
│            Personal Assistant Flow                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User Message                                       │
│       │                                             │
│       ▼                                             │
│  Conversational Memory (History)                    │
│       │                                             │
│       ▼                                             │
│  Agent Reasoning                                    │
│       │                                             │
│       ├──→ Need time? ──→ get_time() Tool           │
│       │                       │                     │
│       └──→ General query ─────┤                     │
│                               │                     │
│                               ▼                     │
│                    Generate Response                 │
│                               │                     │
│                               ▼                     │
│                    Display to User                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Agent 2: Customer Support with Guardrails

```
┌─────────────────────────────────────────────────────┐
│           Customer Support Agent Flow                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Customer Message                                   │
│       │                                             │
│       ▼                                             │
│  ┌─────────────────────┐                            │
│  │   INPUT GUARDRAILS   │                           │
│  │  ├── Content filter  │                           │
│  │  └── Topic scope     │                           │
│  └─────────┬───────────┘                            │
│            │                                        │
│       ┌────┴────┐                                   │
│       │ Valid?  │                                    │
│       └────┬────┘                                   │
│     Yes    │    No ──→ Reject with message           │
│            ▼                                        │
│  Knowledge Base Search                              │
│            │                                        │
│            ▼                                        │
│  Agent Response Generation                          │
│            │                                        │
│            ▼                                        │
│  ┌─────────────────────┐                            │
│  │  OUTPUT GUARDRAILS   │                           │
│  │  └── Pydantic Schema │                           │
│  └─────────┬───────────┘                            │
│            │                                        │
│            ▼                                        │
│  Structured Response                                │
│  (Validated Pydantic Model)                         │
│            │                                        │
│       ┌────┴────┐                                   │
│  Need Approval?                                     │
│       │    Yes ──→ Approval Workflow                 │
│       │ No                                          │
│       ▼                                             │
│  Deliver Response                                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Agent 3: Multi-Agent Research Orchestration

```
┌──────────────────────────────────────────────────────────┐
│          Multi-Agent Research Pipeline                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Research Topic                                          │
│       │                                                  │
│       ▼                                                  │
│  ┌─────────────────────┐                                 │
│  │  RESEARCHER AGENT   │                                 │
│  │  ├── Firecrawl web  │                                 │
│  │  │   search         │                                 │
│  │  ├── Gather sources │                                 │
│  │  └── Compile data   │                                 │
│  └─────────┬───────────┘                                 │
│            │                                             │
│            ▼                                             │
│  ┌─────────────────────┐                                 │
│  │   WRITER AGENT      │                                 │
│  │  ├── Structure info │                                 │
│  │  ├── Draft report   │                                 │
│  │  └── Add citations  │                                 │
│  └─────────┬───────────┘                                 │
│            │                                             │
│            ▼                                             │
│  ┌─────────────────────┐                                 │
│  │   EDITOR AGENT      │                                 │
│  │  ├── Review quality │                                 │
│  │  ├── Polish prose   │                                 │
│  │  └── Final format   │                                 │
│  └─────────┬───────────┘                                 │
│            │                                             │
│            ▼                                             │
│  Markdown Report Output                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

