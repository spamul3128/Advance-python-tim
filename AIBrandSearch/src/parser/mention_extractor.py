"""
Extract brand/tool mentions from LLM answer text using keyword matching.
"""

import re
from typing import Optional


def extract_mentions(
    answer_text: str,
    tracking_keywords: list[str],
) -> tuple[list[str], dict[str, int]]:
    """
    Scan answer text for tracking keywords (case-insensitive).
    Returns (list of found keywords in order of first appearance,
             dict of keyword -> 1-based position in a list, or -1 if not in a list).
    """
    if not answer_text or not tracking_keywords:
        return [], {}

    text_lower = answer_text.lower()
    found: list[str] = []
    seen: set[str] = set()
    mention_positions: dict[str, int] = {}

    # Build regex for each keyword (word boundary friendly, case-insensitive)
    for kw in tracking_keywords:
        if not kw or kw.lower() in seen:
            continue
        pattern = re.escape(kw)
        if re.search(pattern, text_lower, re.IGNORECASE):
            found.append(kw)
            seen.add(kw.lower())

    # Approximate position: look for numbered list items (1. 2. 3.) or bullet lines
    lines = answer_text.split("\n")
    list_position = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Numbered item: 1. 2) 1)
        if re.match(r"^\s*\d+[\.\)]\s", stripped) or re.match(r"^\s*\d+\.\s", stripped):
            list_position += 1
            for kw in tracking_keywords:
                if kw.lower() in stripped.lower() and kw not in mention_positions:
                    mention_positions[kw] = list_position

    for kw in found:
        if kw not in mention_positions:
            mention_positions[kw] = -1

    return found, mention_positions
