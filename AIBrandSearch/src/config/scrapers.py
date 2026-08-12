"""
LLM scraper configuration for Bright Data Web Scraper API.
Scraper IDs from: https://github.com/brightdata/brightdata-agent-showcase/tree/main/agents/seo/unified-llm-scraper
"""

# Base URL for Bright Data Datasets API
BRIGHT_DATA_BASE_URL = "https://api.brightdata.com/datasets/v3"

# LLM scraper IDs and display config (from repo ai_models.py).
# supports_country: if True, we send the "country" field in the trigger body; if False (e.g. Gemini),
# the scraper returns 400 when extra fields are sent, so we omit country for that scraper.
LLM_SCRAPERS = {
    "chatgpt": {
        "id": "gd_m7aof0k82r803d5bjm",
        "name": "ChatGPT",
        "url": "https://chatgpt.com/",
        "color": "#10a37f",
        "supports_country": True,
    },
    "perplexity": {
        "id": "gd_m7dhdot1vw9a7gc1n",
        "name": "Perplexity",
        "url": "https://www.perplexity.ai",
        "color": "#2563eb",
        "supports_country": True,
    },
    "gemini": {
        "id": "gd_mbz66arm2mf9cu856y",
        "name": "Gemini",
        "url": "https://gemini.google.com/",
        "color": "#a855f7",
        "supports_country": False,  # Returns 400 if country or other extra fields are sent
    },
    "grok": {
        "id": "gd_m8ve0u141icu75ae74",
        "name": "Grok",
        "url": "https://grok.com/",
        "color": "#ef4444",
        "supports_country": True,
    },
    "copilot": {
        "id": "gd_m7di5jy6s9geokz8w",
        "name": "Microsoft Copilot",
        "url": "https://copilot.microsoft.com/chats",
        "color": "#06b6d4",
        "supports_country": True,
    },
}

# Ordered list of model keys for consistent UI ordering
LLM_ORDER = ["chatgpt", "perplexity", "gemini", "grok", "copilot"]
