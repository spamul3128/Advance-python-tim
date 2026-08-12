"""
Classify LLM answer shape: ranked_list, narrative, categories, or hybrid.
"""

import re


def classify_answer_shape(answer_text: str) -> str:
    """
    Heuristic classification of answer structure.
    - ranked_list: numbered items (1. 2. 3. or 1) 2) )
    - categories: bullet points or markdown headers with grouped items
    - narrative: mostly flowing prose
    - hybrid: mixed
    """
    if not answer_text or not answer_text.strip():
        return "narrative"

    lines = [ln.strip() for ln in answer_text.split("\n") if ln.strip()]
    if not lines:
        return "narrative"

    numbered_count = 0
    bullet_count = 0
    header_count = 0
    total = len(lines)

    numbered_pattern = re.compile(r"^\s*\d+[\.\)]\s")
    bullet_pattern = re.compile(r"^\s*[-*•]\s")
    header_pattern = re.compile(r"^#{1,6}\s|\*\*[^*]+\*\*:|\b(Here are|Categories?|Types?|Options?):", re.IGNORECASE)

    for line in lines:
        if numbered_pattern.match(line):
            numbered_count += 1
        if bullet_pattern.match(line):
            bullet_count += 1
        if header_pattern.search(line):
            header_count += 1

    # Thresholds: if a significant portion is numbered → ranked_list
    if total > 0 and numbered_count / total >= 0.3:
        if bullet_count / total >= 0.2 or header_count >= 1:
            return "hybrid"
        return "ranked_list"

    if total > 0 and (bullet_count / total >= 0.25 or header_count >= 2):
        if numbered_count >= 1:
            return "hybrid"
        return "categories"

    if numbered_count >= 1 or bullet_count >= 1:
        return "hybrid"

    return "narrative"
