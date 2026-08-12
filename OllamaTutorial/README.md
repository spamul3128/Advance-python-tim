# Ollama Tutorial

Hands-on examples for interacting with **Ollama** — a local LLM runtime — via both **HTTP API** and **Python SDK**.

---

## 📋 Features

- 🌐 **HTTP Streaming** — Direct HTTP requests to Ollama API with streaming
- 🐍 **Python SDK** — Clean Python client usage
- 🏠 **Fully Local** — No cloud APIs needed

---

## 📁 File Structure

| File | Approach | Description |
|------|----------|-------------|
| `sample_request.py` | HTTP API | Raw HTTP POST with streaming JSON response |
| `package.py` | Python SDK | Ollama Python client library usage |

---

## 🚀 Getting Started

### Prerequisites
- [Ollama](https://ollama.ai/) installed and running
- A model pulled: `ollama pull llama3.2`

```bash
cd OllamaTutorial
python sample_request.py    # HTTP approach
python package.py           # SDK approach
```

---

## 📖 Logic Flow

### `sample_request.py` — HTTP API
1. Construct JSON payload with model and prompt
2. POST to `http://localhost:11434/api/generate`
3. Stream response chunks line-by-line
4. Parse JSON and print token-by-token

### `package.py` — Python SDK
1. Import `ollama` package
2. Call `ollama.chat()` with model and messages
3. Receive and display response

---

## 📝 License
Educational project — use freely for learning and reference.
