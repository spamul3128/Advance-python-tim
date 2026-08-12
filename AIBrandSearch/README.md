# AI Brand Search

A **Streamlit dashboard** that compares responses across multiple LLM providers (**ChatGPT, Perplexity, Gemini, Grok, Copilot**) and tracks **keyword mentions** for brand monitoring and competitive analysis.

---

## 📋 Features

- 🤖 **Multi-LLM comparison** — Query ChatGPT, Perplexity, Gemini, Grok, and Copilot
- 🔑 **Keyword tracking** — Track mention frequency and position across responses
- 📊 **Signals table** — Visual keyword mention matrix across providers
- 🔍 **Google SERP** — Compare LLM responses with search engine results
- 🧠 **AI comparative analysis** — OpenAI-powered meta-analysis
- 📦 **Bulk runs** — Execute multiple prompts in sequence
- 💾 **Run history** — Save and reload past sessions

---

## 🏗️ Architecture

```
Streamlit Dashboard → Bright Data Scrapers → [ChatGPT, Perplexity, Gemini, Grok, Copilot]
       │                                              │
       ├─ Signals Table (keyword mentions)            │
       ├─ Response Tabs (raw LLM outputs)             │
       ├─ SERP Results (Google comparison)            │
       └─ AI Comparative Analysis (OpenAI)  ◄─────────┘
```

---

## 📁 File Structure

```
AIBrandSearch/
├── app.py               # Main Streamlit dashboard (536 lines)
├── requirements.txt     # Dependencies
├── src/models.py        # LLMResult, SERPResult, ParseResult dataclasses
├── prompts/             # Prompt templates
└── docs/                # Documentation assets
```

---

## 🚀 Getting Started

```bash
cd AIBrandSearch
pip install -r requirements.txt
streamlit run app.py
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
BRIGHT_DATA_API_KEY=...
```

---

## 📖 Logic Flow

1. **Configure** — Enter prompt, select LLM providers, keywords, country
2. **Execute** — Prompts sent to each LLM via Bright Data scrapers
3. **Parse** — Responses parsed for keyword mentions and positions
4. **Display** — Signals table shows keyword presence per provider
5. **Analyze** — OpenAI generates comparative analysis
6. **SERP** — Google results fetched for comparison

---

## 📦 Dependencies
`streamlit>=1.30.0`, `httpx>=0.25.0`, `python-dotenv`, `pandas>=2.0.0`, `openai>=1.0.0`

---

## 📝 License
Educational project — use freely for learning and reference.
