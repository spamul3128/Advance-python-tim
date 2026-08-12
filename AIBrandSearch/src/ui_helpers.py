"""
UI helpers: highlight keywords in text, build export JSON.
"""

import html
import json
import re
from dataclasses import asdict
from typing import Any

from src.models import LLMResult, ParsedSignals, SERPResult


def highlight_keywords(text: str, keywords: list[str], css_class: str = "mention") -> str:
    """
    Wrap each keyword (case-insensitive) in a span with the given CSS class.
    Escapes HTML in the original text.
    """
    if not text or not keywords:
        return html.escape(text)

    escaped = html.escape(text)
    # Sort by length descending so longer phrases get matched first
    sorted_kw = sorted(
        [k for k in keywords if k and k.strip()],
        key=len,
        reverse=True,
    )
    for kw in sorted_kw:
        if not kw:
            continue
        pattern = re.escape(kw)
        # Replace case-insensitively; wrap in span
        escaped = re.sub(
            f"({pattern})",
            f'<span class="{css_class}">\\1</span>',
            escaped,
            flags=re.IGNORECASE,
        )
    return escaped


def build_export_json(
    results: list[LLMResult],
    parsed: list[ParsedSignals],
    serp_results: list[SERPResult] | None,
    prompt: str,
    country: str | None,
) -> str:
    """Build a single JSON string for download (run artifact)."""
    payload = {
        "prompt": prompt,
        "country": country,
        "timestamp": results[0].timestamp if results else None,
        "llm_results": [asdict(r) for r in results],
        "parsed_signals": [asdict(p) for p in parsed],
        "serp_results": [asdict(s) for s in (serp_results or [])],
    }
    # asdict may not serialize raw_payload if it has non-serializable items
    for i, r in enumerate(payload["llm_results"]):
        if "raw_payload" in r and r["raw_payload"]:
            try:
                json.dumps(r["raw_payload"])
            except (TypeError, ValueError):
                r["raw_payload"] = {"_note": "omitted (non-JSON-safe)"}
    return json.dumps(payload, indent=2)
