# LangChain Transformers Python

**Text summarization and Q&A** using **HuggingFace transformer models** integrated with **LangChain** — runs fully local with GPU acceleration.

---

## 📋 Features

- 📝 **Text Summarization** — BART-large-cnn for abstractive summaries
- ❓ **Question Answering** — RoBERTa-base-squad2 for Q&A on summaries
- 📏 **Configurable Length** — Short, medium, or long summaries
- ⚡ **GPU Acceleration** — CUDA device 0 support
- 🔗 **LangChain Integration** — PromptTemplate and chain syntax

---

## 🏗️ Architecture

```
User Text → BART Summarizer → Summary
                                 │
User Question → RoBERTa QA Model ─┘ → Answer
```

### Models Used
| Model | Task | Source |
|-------|------|--------|
| `facebook/bart-large-cnn` | Summarization | HuggingFace |
| `facebook/bart-large` | Refinement | HuggingFace |
| `deepset/roberta-base-squad2` | Question Answering | HuggingFace |

---

## 🚀 Getting Started

```bash
cd Langchain-Transformers-Python
pip install -r requirements.txt
python main.py
```

---

## 📖 Logic Flow

1. **Input** — User enters text to summarize
2. **Summarize** — BART-large-cnn generates abstractive summary
3. **Refine** — Optional refinement pass with BART-large
4. **Display** — Summary shown to user
5. **Q&A Loop** — User asks questions about the summary
6. **Answer** — RoBERTa extracts answers from the summary context

---

## 📦 Dependencies
`transformers`, `langchain`, `huggingface-hub`, `torch`

---

## 📝 License
Educational project — use freely for learning and reference.
