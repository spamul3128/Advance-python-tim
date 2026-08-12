# Amazon Price Competitor Analysis LLM

A **Streamlit dashboard** for scraping Amazon product data by ASIN, discovering competitors, and generating **LLM-powered competitive analysis** reports.

---

## 📋 Features

- 🔍 **ASIN Lookup** — Scrape product details by Amazon Standard Identification Number
- 🌍 **Geo-targeting** — Localized results by country/region
- 🏆 **Competitor Discovery** — Automatically find and analyze competing products
- 🧠 **LLM Analysis** — AI-powered pricing and positioning insights
- 🗄️ **TinyDB Storage** — Lightweight local JSON-based persistence
- 📊 **Product Cards** — Visual display with images and pricing

---

## 🏗️ Architecture

```
Streamlit UI → Scraper Service → Amazon Products → TinyDB Storage
                                                        │
                                                   LLM Analysis
                                                   (Competitive Insights)
```

---

## 🚀 Getting Started

```bash
cd AmazonPriceCompetitorAnalysisLLM
uv sync
uv run streamlit run main.py
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
BRIGHT_DATA_API_KEY=...
```

---

## 📖 Logic Flow

1. **Input** — User enters ASIN and target country
2. **Scrape** — Product data fetched from Amazon
3. **Store** — Data persisted to TinyDB
4. **Competitors** — Related products discovered and scraped
5. **Display** — Product cards rendered (10 per page)
6. **Analyze** — LLM generates competitive insights

### Key Functions
| Function | Purpose |
|----------|---------|
| `scrape_and_store_product()` | Fetch Amazon product by ASIN |
| `fetch_and_store_competitors()` | Discover competing products |
| `analyze_competitors()` | LLM-powered competitive analysis |

---

## 📦 Dependencies
`langchain>=0.3.27`, `langchain-openai>=0.3.33`, `openai>=1.107.2`, `streamlit>=1.49.1`, `tinydb>=4.8.2`, `python-dotenv>=1.1.1`

---

## 📝 License
Educational project — use freely for learning and reference.
