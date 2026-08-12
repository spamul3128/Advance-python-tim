# Local AI Agent With RAG

A **local-first RAG system** using **Ollama** (Llama 3.2) for inference and a custom vector retriever — no cloud APIs required.

---

## 📋 Features

- 🏠 **Fully Local** — Runs entirely on your machine via Ollama
- 🧠 **RAG Pipeline** — Vector-based retrieval before answering
- 🍕 **Domain-Specific** — Pre-loaded with pizza restaurant review data
- 💬 **Conversational** — Interactive Q&A with context injection

---

## 🏗️ Architecture

```
User Query → Vector Retriever → Relevant Reviews → LLM Prompt → Ollama (Llama 3.2) → Answer
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+, [Ollama](https://ollama.ai/) running, `ollama pull llama3.2`

```bash
cd LocalAIAgentWithRAG
pip install -r requirements.txt
python main.py
```

---

## 📖 Logic Flow

1. **Startup** — Vector store initialized with review data
2. **Query** — User asks a question
3. **Retrieval** — Most relevant reviews found via vector search
4. **Context** — Reviews injected into LLM prompt template
5. **Inference** — Ollama runs Llama 3.2 locally
6. **Response** — Context-aware answer displayed

---

## 📦 Dependencies
`langchain-ollama`, `langchain`, `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.
