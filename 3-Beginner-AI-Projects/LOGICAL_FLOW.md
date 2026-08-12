# 3 Beginner AI Projects — Logical Flow

## 📋 Project Overview
Three beginner-friendly AI projects: a ReAct Agent, an AI Resume Critiquer, and an Image Classifier.

---

## 🔄 Project 1: ReAct Agent (Tool-Calling AI Assistant)

```
┌─────────────────────────────────────────────────────┐
│                  ReAct Agent Flow                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User Input (CLI)                                   │
│       │                                             │
│       ▼                                             │
│  LangGraph ReAct Agent                              │
│       │                                             │
│       ▼                                             │
│  ┌─────────────────────┐                            │
│  │   Agent Reasoning    │                           │
│  │   (Think → Act)      │                           │
│  └─────────┬───────────┘                            │
│            │                                        │
│       ┌────┴────┐                                   │
│       ▼         ▼                                   │
│  @calculator  @say_hello                            │
│   (math)      (greeting)                            │
│       │         │                                   │
│       └────┬────┘                                   │
│            ▼                                        │
│  Tool Execution Result                              │
│            │                                        │
│            ▼                                        │
│  Response Generation                                │
│            │                                        │
│            ▼                                        │
│  Display to User ──→ Loop until "quit"              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Project 2: AI Resume Critiquer

```
┌─────────────────────────────────────────────────────┐
│              Resume Critiquer Flow                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Streamlit Web UI                                   │
│       │                                             │
│       ▼                                             │
│  File Upload (PDF / TXT)                            │
│       │                                             │
│       ├──── PDF? ──→ PyPDF2 Text Extraction         │
│       │                    │                        │
│       ├──── TXT? ──→ Direct Text Decode             │
│       │                    │                        │
│       └────────────────────┤                        │
│                            ▼                        │
│                  Extracted Text                      │
│                            │                        │
│                            ▼                        │
│              User Specifies Target Role              │
│                            │                        │
│                            ▼                        │
│              OpenAI API Analysis                     │
│              (System Prompt + Resume)                │
│                            │                        │
│                            ▼                        │
│              Structured Feedback Display             │
│              • Strengths                             │
│              • Weaknesses                            │
│              • Suggestions                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Project 3: Image Classifier

```
┌─────────────────────────────────────────────────────┐
│              Image Classifier Flow                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Streamlit Web UI                                   │
│       │                                             │
│       ▼                                             │
│  Image Upload (JPG/PNG)                             │
│       │                                             │
│       ▼                                             │
│  Preprocessing                                      │
│  ├── Resize to 224×224                              │
│  ├── Normalize pixel values                         │
│  └── Prepare input tensor                           │
│       │                                             │
│       ▼                                             │
│  MobileNetV2 (Pre-trained)                          │
│  └── ImageNet weights                               │
│       │                                             │
│       ▼                                             │
│  Model Inference                                    │
│       │                                             │
│       ▼                                             │
│  decode_predictions()                               │
│       │                                             │
│       ▼                                             │
│  Display Top-3 Results                              │
│  ├── Class Name 1 — Confidence %                    │
│  ├── Class Name 2 — Confidence %                    │
│  └── Class Name 3 — Confidence %                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

