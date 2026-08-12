# 3 Beginner AI Projects

Three hands-on AI projects that progressively introduce **LLM agents**, **document analysis**, and **computer vision** — ideal for developers starting their AI journey.

---

## 📋 Projects Overview

| # | Project | Stack | Description |
|---|---------|-------|-------------|
| 1 | **ReAct Agent** | LangGraph + OpenAI | Tool-calling AI agent with calculator and greeting tools |
| 2 | **Resume Critiquer** | Streamlit + OpenAI | Upload a resume (PDF/TXT), get AI-powered feedback |
| 3 | **Image Classifier** | Streamlit + TensorFlow | Upload an image, get real-time MobileNetV2 predictions |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- OpenAI API key (for Projects 1 & 2)

### Installation
```bash
cd 3-Beginner-AI-Projects

# Project 1
cd project1
uv sync          # or: pip install langchain langgraph langchain-openai python-dotenv
python main.py

# Project 2
cd project2
uv sync          # or: pip install streamlit PyPDF2 openai python-dotenv
streamlit run main.py

# Project 3
cd project3
uv sync          # or: pip install streamlit tensorflow Pillow opencv-python numpy
streamlit run main.py
```

### Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-...
```

---

## 📖 Project Details

### Project 1 — ReAct Agent (`project1/main.py`)
**What it does:** An interactive CLI agent that can call tools to answer questions.

**Architecture:**
```
User Input → LangGraph ReAct Agent → Tool Selection → Tool Execution → Response
                                         ↓
                              ┌──────────┴──────────┐
                              │  calculator(a, b)    │
                              │  say_hello(name)     │
                              └──────────────────────┘
```

**Key Concepts:**
- `@tool` decorator to define callable tools
- `create_react_agent()` from LangGraph for reasoning + acting
- `ChatOpenAI` (GPT-4o-mini) as the base LLM
- Interactive loop with conversation history

**Logic Flow:**
1. User enters a query
2. Agent reasons about which tool to call
3. Tool executes and returns result
4. Agent formulates final response
5. Loop continues until user types "quit"

---

### Project 2 — AI Resume Critiquer (`project2/main.py`)
**What it does:** A Streamlit web app that analyzes uploaded resumes and provides targeted feedback.

**Architecture:**
```
File Upload (PDF/TXT) → Text Extraction → OpenAI GPT-4o-mini → Structured Feedback
      ↓                      ↓                    ↓
  Streamlit UI         PyPDF2 / .read()      Role-specific prompt
```

**Key Concepts:**
- PDF text extraction with `PyPDF2`
- Dynamic system prompts based on target role
- Streaming OpenAI responses
- Streamlit file uploader and text display

**Logic Flow:**
1. User uploads a PDF or TXT resume
2. Text is extracted from the document
3. User specifies the target job role
4. OpenAI analyzes the resume for that role
5. Feedback is displayed with formatting suggestions

---

### Project 3 — Image Classifier (`project3/main.py`)
**What it does:** A web app that classifies uploaded images using a pre-trained MobileNetV2 neural network.

**Architecture:**
```
Image Upload → Preprocessing (224×224) → MobileNetV2 → decode_predictions → Top 3 Results
     ↓               ↓                       ↓                                    ↓
 Streamlit UI    NumPy array         TensorFlow/Keras                     Label + Confidence
```

**Key Concepts:**
- Transfer learning with `MobileNetV2` (pre-trained on ImageNet)
- Image preprocessing: resize to 224×224, normalize pixel values
- `decode_predictions()` for human-readable labels
- Top-3 prediction display with confidence scores

**Logic Flow:**
1. User uploads an image (JPG, PNG)
2. Image is resized and preprocessed for the model
3. MobileNetV2 runs inference
4. Top 3 predictions with confidence percentages are displayed
5. Original image is shown alongside results

---

## 🏗️ Project Structure
```
3-Beginner-AI-Projects/
├── project1/
│   ├── main.py          # ReAct agent with tools
│   └── pyproject.toml
├── project2/
│   ├── main.py          # Resume critiquer app
│   └── pyproject.toml
└── project3/
    ├── main.py          # Image classifier app
    └── pyproject.toml
```

---

## 📝 License
Educational project — use freely for learning and reference.

