# API For Your LLM

A **FastAPI REST API** that wraps a local **Ollama LLM** (Mistral model) with **API key authentication** and a **credit-based usage system**.

---

## 📋 Features

- 🔑 **API Key Auth** — Header-based authentication via `x-api-key`
- 💳 **Credit System** — Usage tracking with credit deduction per request
- 🤖 **Local LLM** — Powered by Ollama (Mistral model)
- ⚡ **FastAPI** — High-performance async REST endpoints

---

## 🏗️ Architecture

```
Client → POST /generate (x-api-key) → FastAPI → verify_api_key() → deduct credit → ollama.chat() → Response
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+, [Ollama](https://ollama.ai/) running, `ollama pull mistral`

```bash
cd API-For-Your-LLM
pip install -r requirements.txt
uvicorn main:app --reload
```

### Test
```bash
curl -X POST http://localhost:8000/generate \
  -H "x-api-key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing"}'
```

---

## 📖 API Reference

### `POST /generate`
| Header | Required | Description |
|--------|----------|-------------|
| `x-api-key` | Yes | API key for authentication |

**Request:** `{"prompt": "Your question"}` · **Response:** `{"response": "Generated text..."}`

---

## 📖 Logic Flow

1. Client sends POST with prompt and API key
2. `verify_api_key()` validates the key
3. Credit check and deduction
4. Forward prompt to Ollama's Mistral model
5. Return generated text as JSON

---

## 📦 Dependencies
`fastapi`, `uvicorn`, `ollama`, `python-dotenv`, `requests`

---

## 📝 License
Educational project — use freely for learning and reference.
