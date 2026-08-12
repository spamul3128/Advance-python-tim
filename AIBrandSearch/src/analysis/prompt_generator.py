"""
Generate batch run prompts and tracking keywords from a topic using OpenAI.
Returns prompts list and tracking keywords for use with the bulk runner.
Batch-generated prompts get a random country from an expanded list (incl. MY, ID, CN, etc.).
"""

import json
import random
import re
from pathlib import Path

# Countries used when randomizing batch-generated prompts (2-letter codes).
# Includes Malaysia, Indonesia, China, and other major markets.
BATCH_COUNTRIES = [
    "us",
    "uk",
    "de",
    "fr",
    "ca",
    "au",
    "my",   # Malaysia
    "id",   # Indonesia
    "cn",   # China
    "jp",   # Japan
    "in",   # India
    "sg",   # Singapore
    "kr",   # South Korea
    "br",   # Brazil
    "mx",   # Mexico
    "es",   # Spain
    "it",   # Italy
    "nl",   # Netherlands
    "pl",   # Poland
    "th",   # Thailand
    "vn",   # Vietnam
    "ph",   # Philippines
]


def generate_prompts_from_topic(
    topic: str,
    *,
    api_key: str,
    count: int = 10,
    default_country: str = "us",
    model: str = "gpt-4",
) -> tuple[list[dict[str, str]], list[str], str | None]:
    """
    Use OpenAI to generate search-style prompts and tracking keywords for the topic.
    Returns (prompts list, tracking_keywords list, error_message or None).
    """
    if not api_key or not api_key.strip():
        return [], [], "No OpenAI API key provided. Set OPENAI_API_KEY in your .env file."

    topic = (topic or "").strip()
    if not topic:
        return [], [], "Enter a topic to generate prompts."

    count = max(1, min(count, 50))
    system = """You generate search queries and tracking keywords for a competitive/marketing research tool.
Output only a single JSON object with two keys:
- "prompts": an array of objects, each with "prompt" (search query string) and "country" (e.g. "us", "uk", "de").
- "tracking_keywords": an array of 10–20 strings: brand names, product names, or tool names that are relevant to the topic and that we want to detect in search/LLM answers (e.g. for "SEO tools" you might include "SEMrush", "Ahrefs", "Moz", "Bright Data").
Generate diverse, realistic prompts. No commentary, only the JSON object."""

    user = f"""Topic: {topic}

Generate exactly {count} search prompts and 10–20 tracking keywords. Example format:
{{"prompts": [{{"prompt": "First query here", "country": "us"}}, {{"prompt": "Second query", "country": "uk"}}], "tracking_keywords": ["Brand A", "Tool B", "Product C"]}}

Output only the JSON object, nothing else."""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key.strip())
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_completion_tokens=2000,
        )
        choice = response.choices[0] if response.choices else None
        if not choice or not choice.message or not choice.message.content:
            return [], [], "OpenAI returned an empty response. Try a different model."

        content = choice.message.content
        if isinstance(content, list):
            content = "".join(
                p.get("text", "") if isinstance(p, dict) else str(p) for p in content
            )
        text = (content or "").strip()

        parsed_prompts, parsed_keywords = _parse_prompts_and_keywords_json(text, default_country)
        if not parsed_prompts:
            return [], [], "Could not parse prompts from model response. Try again or use a different topic."
        # Assign a random country from the expanded list to each prompt for geographic diversity.
        for item in parsed_prompts:
            item["country"] = random.choice(BATCH_COUNTRIES)
        return parsed_prompts, parsed_keywords, None
    except Exception as e:
        return [], [], f"Generation failed: {e}"


def _parse_prompts_and_keywords_json(
    text: str, default_country: str
) -> tuple[list[dict[str, str]], list[str]]:
    """Extract prompts list and tracking_keywords list from model output."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    prompts_out: list[dict[str, str]] = []
    keywords_out: list[str] = []

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            if "prompts" in data:
                prompts_out = _normalize_prompt_list(data["prompts"], default_country)
            if "tracking_keywords" in data and isinstance(data["tracking_keywords"], list):
                keywords_out = [str(k).strip() for k in data["tracking_keywords"] if k and str(k).strip()]
        elif isinstance(data, list):
            prompts_out = _normalize_prompt_list(data, default_country)
    except json.JSONDecodeError:
        pass

    if not prompts_out:
        match = re.search(r"\[[\s\S]*\]", text)
        if match:
            try:
                data = json.loads(match.group(0))
                prompts_out = _normalize_prompt_list(data, default_country)
            except json.JSONDecodeError:
                pass
    return prompts_out, keywords_out


def _normalize_prompt_list(
    items: list, default_country: str
) -> list[dict[str, str]]:
    out = []
    for item in items:
        if isinstance(item, str):
            out.append({"prompt": item.strip(), "country": default_country})
        elif isinstance(item, dict):
            p = (item.get("prompt") or item.get("query") or "").strip()
            if p:
                out.append({
                    "prompt": p,
                    "country": (item.get("country") or default_country).lower() or default_country,
                })
    return out


def save_prompts_to_file(
    prompts: list[dict[str, str]],
    topic: str,
    tracking_keywords: list[str] | None = None,
) -> Path:
    """Save prompts and optional tracking_keywords to prompts/generated-<slug>.json. Returns the path."""
    slug = re.sub(r"[^\w\-]+", "-", topic.lower())[:40].strip("-") or "prompts"
    prompts_dir = Path(__file__).resolve().parent.parent.parent / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    path = prompts_dir / f"generated-{slug}-{ts}.json"
    payload: dict = {"prompts": prompts}
    if tracking_keywords:
        payload["tracking_keywords"] = tracking_keywords
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
