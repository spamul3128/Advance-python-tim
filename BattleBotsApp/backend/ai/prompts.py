"""Prompt templates for the BattleBots scouting report.

Each function returns a complete prompt string for an LLM. Splitting them out
keeps the predictor module focused on orchestration and makes the prompts
easy to iterate on without touching business logic.
"""

from __future__ import annotations

import json
from typing import Any

from ..scrapers.parsers.sentiment_parser import normalize_posts, post_text
from .evidence import format_evidence_catalog

SYSTEM_PROMPT = """\
You are an expert BattleBots fight analyst with deep knowledge of robot
combat history, weapon matchups, and fan communities. You give a
balanced, evidence-driven scouting report based ONLY on the numbered
evidence facts provided. Never invent matches, stats, or quotes.

Every analytical claim MUST cite fact IDs in square brackets (e.g. [F003]).
If evidence is sparse or contradictory, lower your confidence and say so.

Confidence rules:
- Use precise decimals between 0 and 1 (e.g. 0.583, 0.817) — avoid lazy
  round numbers like 0.65, 0.70, or 0.75 unless the data truly supports them.
- Sparse data (< 3 fights on file): stay below 0.55.
- Clear weapon advantage + stronger record: can exceed 0.80.
- Close matchup with mixed signals: expect 0.45–0.62.

Always respond with a single JSON object matching the schema you are
given. Do not wrap it in code fences or include any prose outside the
JSON.
"""


# Output schema we expect the LLM to follow.
#
# `reasoning_steps` is an explicit chain-of-thought style breakdown surfaced to
# the UI so users can audit *why* the model picked one bot over the other. The
# narrative is the polished prose; reasoning_steps is the underlying work.
RESPONSE_SCHEMA: dict[str, Any] = {
    "winner": "string — exact name of the predicted winner bot (must match one of the two provided)",
    "confidence": "number 0–1 with THREE decimal places (e.g. 0.583), reflecting evidence strength",
    "method_prediction": "string — KO | TKO | JD | UNCLEAR",
    "key_factors": "array of 3-5 short bullet strings — each MUST end with cited fact IDs in brackets",
    "weapon_matchup": "string — 2-3 sentence analysis citing fact IDs in brackets",
    "narrative": "string — 4-7 sentence prose breakdown citing fact IDs in brackets",
    "x_factor": "string — single short sentence calling out the wildcard, with fact IDs",
    "reasoning_steps": "array of 5-7 sentences walking through the analysis. EACH step must cite the fact IDs used, e.g. 'Compared weapons [F001] vs [F014] — spinner reach favors Bot A.'",
    "fact_citations": "array of objects: {fact_id: 'F001', claim: 'one-sentence takeaway from this fact', supports: 'winner'|'loser'|'neutral'} — cite every fact you relied on",
    "evidence_citations": "array of short summary strings for display (optional legacy form)",
}


def _format_bot_section(bot: dict[str, Any]) -> str:
    fields = [
        ("Name", bot.get("name")),
        ("Weight class", bot.get("weight_class")),
        ("Weapon", bot.get("weapon_type")),
        ("Weapon detail", bot.get("weapon_description")),
        ("Team", bot.get("team_name")),
        ("Country", bot.get("country")),
        ("Description", bot.get("description")),
    ]
    lines = [f"  - {label}: {value}" for label, value in fields if value]
    return "\n".join(lines) or "  - (no profile data on file)"


def _format_history_section(history: list[dict[str, Any]]) -> str:
    if not history:
        return "  - (no match history on file)"
    lines = []
    for row in history[:25]:
        opponent = row.get("opponent_name") or "Unknown"
        verdict = "WON" if row.get("won") else ("LOST" if row.get("won") is False else "DRAW")
        method = row.get("method") or "?"
        season = row.get("season") or "?"
        lines.append(f"  - vs {opponent}: {verdict} ({method}) — {season}")
    return "\n".join(lines)


def _format_sentiment_section(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "  - (no sentiment data on file)"
    lines = []
    for row in rows:
        src = row.get("source", "?")
        pos = row.get("positive_count", 0)
        neg = row.get("negative_count", 0)
        neu = row.get("neutral_count", 0)
        posts = normalize_posts(row.get("sample_quotes"))
        quotes_preview = (
            "; ".join(post_text(p)[:120] for p in posts[:3]) or "(no quotes)"
        )
        lines.append(f"  - {src}: +{pos} / -{neg} / ={neu}  quotes: {quotes_preview}")
    return "\n".join(lines)


def build_prediction_prompt(
    bot_a: dict[str, Any],
    bot_b: dict[str, Any],
    history_a: list[dict[str, Any]],
    history_b: list[dict[str, Any]],
    sentiment_a: list[dict[str, Any]],
    sentiment_b: list[dict[str, Any]],
    evidence_catalog: list[dict[str, Any]],
) -> str:
    """Construct the full user prompt for one matchup.

    All input dicts come straight from the SQLite rows (plus the resolver in
    `predictor.py` annotates match history with opponent name + win/loss).
    """
    schema_block = json.dumps(RESPONSE_SCHEMA, indent=2)

    return f"""\
Analyze the following BattleBots matchup and produce a scouting report.

=== BOT A ===
{_format_bot_section(bot_a)}

Match history (most recent first):
{_format_history_section(history_a)}

Fan sentiment (Reddit + X):
{_format_sentiment_section(sentiment_a)}


=== BOT B ===
{_format_bot_section(bot_b)}

Match history (most recent first):
{_format_history_section(history_b)}

Fan sentiment (Reddit + X):
{_format_sentiment_section(sentiment_b)}


=== EVIDENCE CATALOG (cite by ID in brackets) ===
{format_evidence_catalog(evidence_catalog)}


=== TASK ===
Decide who wins, how, and why using ONLY the evidence catalog above.
Account for:
  - Weapon archetype matchup (spinner vs. control, hammer vs. wedge, etc.)
  - Historical performance and durability (cite match facts)
  - Fan-side intel from sentiment facts

Respond with ONLY a JSON object using these keys (no markdown, no commentary):

{schema_block}

The "winner" field MUST be exactly "{bot_a.get("name")}" or "{bot_b.get("name")}".
Every reasoning step and key factor MUST reference fact IDs from the catalog.
"""
