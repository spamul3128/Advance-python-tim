# Deepgram Voice Agent

A **real-time voice-based pharmacy assistant** using **Deepgram's agentic AI** with **Twilio** integration for phone call handling.

---

## 📋 Features

- 🎙️ **Real-time voice interaction** via WebSocket audio streaming
- 💊 **Pharmacy operations** — Drug info, order placement, order lookup
- 📞 **Twilio integration** — Handle actual phone calls
- 🔄 **Barge-in support** — User can interrupt the agent mid-response
- 🛠️ **Function calling** — Agent triggers domain-specific functions

---

## 🏗️ Architecture

```
Phone Call → Twilio → WebSocket → Deepgram Agent → Function Calls → Pharmacy DB
                                      │                                   │
                                 Audio Stream                    ┌────────┴────────┐
                                 (bidirectional)                 │ get_drug_info() │
                                                                 │ place_order()   │
                                                                 │ lookup_order()  │
                                                                 └─────────────────┘
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `main.py` | WebSocket handlers for Twilio ↔ Deepgram integration (177 lines) |
| `pharmacy_functions.py` | Pharmacy function handlers: drug info, orders (88 lines) |
| `config.json` | Agent configuration and settings |
| `pyproject.toml` | Dependencies |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+, Deepgram API key, Twilio account

```bash
cd DeepgramVoiceAgent
uv sync
```

### Environment Variables (.env)
```env
DEEPGRAM_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

### Run
```bash
uv run python main.py
```
Starts WebSocket server on `localhost:5000`.

---

## 📖 Logic Flow

1. **Phone call** arrives via Twilio
2. **WebSocket** connection established between Twilio and server
3. **Audio stream** forwarded to Deepgram for speech-to-text
4. **Agent processes** the transcribed text
5. **Function calls** triggered when agent needs pharmacy data
6. **Response audio** streamed back via Deepgram TTS → Twilio → caller

### Pharmacy Functions
| Function | Description |
|----------|-------------|
| `get_drug_info(drug_name)` | Look up drug details from in-memory database |
| `place_order(drug, quantity)` | Create a new pharmacy order |
| `lookup_order(order_id)` | Check status of existing order |

---

## 📦 Dependencies
`websockets`, `deepgram-sdk`, `twilio`, `python-dotenv`

---

## 📝 License
Educational project — use freely for learning and reference.
