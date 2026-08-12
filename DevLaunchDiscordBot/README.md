# DevLaunch Discord Bot

A **Discord bot** for server analytics with **message storage**, **AI-powered summarization**, and **Q&A** over message history.

---

## 📋 Features

- 📊 **Message Logging** — Comprehensive metadata capture for all messages
- 🕐 **History Retrieval** — `!history` with filters (user, channel, timeframe)
- 🧠 **AI Summarization** — `!summarize` filtered messages with OpenAI
- ❓ **AI Q&A** — `!ask` questions about message history with LLM context
- 🔒 **Admin Controls** — Permission-checked commands
- 🗄️ **PostgreSQL** — Persistent message and metadata storage
- 📱 **Discord Embeds** — Rich formatted responses

---

## 🏗️ Architecture

```
Discord Server → Bot (discord.py) → PostgreSQL (message storage)
                       │
                  ┌────┼────┐
                  ▼    ▼    ▼
              !history  !summarize  !ask
                  │         │         │
                  ▼         ▼         ▼
              DB Query   DB Query   DB Query
                         + OpenAI   + OpenAI
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `bot.py` | Main bot with commands and message logging (475 lines) |
| `main.py` | Entry point |
| `database.py` | PostgreSQL connection and queries |
| `llm.py` | OpenAI integration for summarization and Q&A |
| `utils.py` | Helper utilities |
| `init_db.py` | Database initialization |
| `reset_db.py` | Database reset utility |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+, PostgreSQL, Discord Bot Token, OpenAI API key

```bash
cd DevLaunchDiscordBot
uv sync    # or: pip install -r requirements.txt
```

### Environment Variables (.env)
```env
DISCORD_TOKEN=...
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
```

### Run
```bash
python bot.py
```

---

## 📖 Commands

| Command | Description | Access |
|---------|-------------|--------|
| `!history [user] [channel] [time]` | Retrieve past messages with filters | All |
| `!summarize [filters]` | AI summary of filtered messages | Admin |
| `!ask <question>` | Ask questions about message history | Admin |

### Time Filters
`1h` (1 hour), `24h` (24 hours), `7d` (7 days), `30m` (30 minutes)

---

## 📖 Logic Flow

1. **Message arrives** → Bot captures full metadata and stores in PostgreSQL
2. **Command received** → Parse filters (user, channel, timeframe)
3. **Database query** → Retrieve matching messages
4. **AI processing** (for summarize/ask) → Context injected into OpenAI prompt
5. **Response** → Formatted Discord embed sent to channel

---

## 📦 Dependencies
`discord.py`, `python-dotenv`, `asyncpg`, `openai`

---

## 📝 License
Educational project — use freely for learning and reference.
