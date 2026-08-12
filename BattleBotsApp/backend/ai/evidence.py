"""Build a numbered evidence catalog and calibrate prediction confidence.

The catalog gives every scraped fact a stable ID (F001, F002, …) with a
source URL so the LLM can cite them and the UI can link back to the origin.
"""

from __future__ import annotations

from typing import Any

from ..scrapers.parsers.sentiment_parser import normalize_posts, post_text


def build_evidence_catalog(
    *,
    bot_a: dict[str, Any],
    bot_b: dict[str, Any],
    history_a: list[dict[str, Any]],
    history_b: list[dict[str, Any]],
    sentiment_a: list[dict[str, Any]],
    sentiment_b: list[dict[str, Any]],
    rag_a: list[dict[str, Any]] | None = None,
    rag_b: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return ordered facts the LLM must cite by ID."""
    facts: list[dict[str, Any]] = []
    counter = 1

    def add(
        *,
        category: str,
        bot: str,
        label: str,
        detail: str,
        source_url: str | None = None,
        source_name: str | None = None,
    ) -> str:
        nonlocal counter
        fact_id = f"F{counter:03d}"
        counter += 1
        facts.append(
            {
                "id": fact_id,
                "category": category,
                "bot": bot,
                "label": label,
                "detail": detail,
                "source_url": source_url,
                "source_name": source_name or _source_name(source_url),
            }
        )
        return fact_id

    for side, bot, history, sentiment, rag_chunks in (
        ("A", bot_a, history_a, sentiment_a, rag_a or []),
        ("B", bot_b, history_b, sentiment_b, rag_b or []),
    ):
        name = bot.get("name") or f"Bot {side}"
        wiki = bot.get("source_url")

        if bot.get("weapon_type") or bot.get("weapon_description"):
            weapon = bot.get("weapon_type") or "unknown"
            detail = bot.get("weapon_description") or weapon
            add(
                category="profile",
                bot=side,
                label=f"{name} — weapon",
                detail=f"{weapon}: {detail}",
                source_url=wiki,
                source_name="BattleBots Wiki",
            )

        if bot.get("team_name") or bot.get("country"):
            add(
                category="profile",
                bot=side,
                label=f"{name} — team",
                detail=f"{bot.get('team_name') or '?'} ({bot.get('country') or '?'})",
                source_url=wiki,
                source_name="BattleBots Wiki",
            )

        wins = sum(1 for row in history if row.get("won") is True)
        losses = sum(1 for row in history if row.get("won") is False)
        draws = sum(1 for row in history if row.get("won") is None)
        if history:
            add(
                category="record",
                bot=side,
                label=f"{name} — fight record",
                detail=f"{wins}W-{losses}L-{draws}D across {len(history)} recorded fights",
                source_url=wiki,
                source_name="BattleBots Wiki",
            )

        for row in history[:12]:
            opponent = row.get("opponent_name") or "Unknown"
            verdict = (
                "WIN"
                if row.get("won") is True
                else ("LOSS" if row.get("won") is False else "DRAW")
            )
            method = row.get("method") or "?"
            season = row.get("season") or "?"
            round_name = row.get("round") or ""
            round_bit = f" ({round_name})" if round_name else ""
            add(
                category="match",
                bot=side,
                label=f"{name} vs {opponent}",
                detail=f"{verdict} via {method} — {season}{round_bit}",
                source_url=row.get("source_url") or wiki,
                source_name=_match_source_name(row.get("source_url")),
            )

        for row in sentiment:
            src = row.get("source") or "fan"
            pos = row.get("positive_count", 0)
            neg = row.get("negative_count", 0)
            neu = row.get("neutral_count", 0)
            add(
                category="sentiment",
                bot=side,
                label=f"{name} — {src} sentiment aggregate",
                detail=f"+{pos} / -{neg} / ={neu} classified posts",
                source_name=src.title(),
            )

            if rag_chunks:
                for chunk in rag_chunks:
                    meta = chunk.get("metadata") or {}
                    chunk_type = chunk.get("chunk_type") or "post"
                    sim = chunk.get("similarity")
                    sim_bit = f" (relevance {sim:.2f})" if sim is not None else ""
                    add(
                        category="sentiment",
                        bot=side,
                        label=f"{name} — Reddit {chunk_type}{sim_bit}",
                        detail=(chunk.get("text") or "")[:240],
                        source_url=chunk.get("url"),
                        source_name=meta.get("subreddit")
                        and f"r/{meta['subreddit']}"
                        or "Reddit",
                    )
            else:
                for post in normalize_posts(row.get("sample_quotes"))[:5]:
                    title = post.get("title") or post_text(post)
                    body = (post.get("body") or "").strip()
                    detail = title if not body else f"{title} — {body[:160]}"
                    add(
                        category="sentiment",
                        bot=side,
                        label=f"{name} — {src} post",
                        detail=detail[:240],
                        source_url=post.get("url"),
                        source_name=post.get("subreddit")
                        and f"r/{post['subreddit']}"
                        or src.title(),
                    )

    return facts


def format_evidence_catalog(facts: list[dict[str, Any]]) -> str:
    """Render the catalog for the LLM prompt."""
    if not facts:
        return "  - (no evidence on file)"
    lines = []
    for fact in facts:
        url_bit = f" → {fact['source_url']}" if fact.get("source_url") else ""
        lines.append(
            f"  [{fact['id']}] ({fact['category']}, Bot {fact['bot']}) "
            f"{fact['label']}: {fact['detail']}{url_bit}"
        )
    return "\n".join(lines)


def refine_confidence(
    llm_confidence: float,
    *,
    winner_name: str,
    bot_a_name: str,
    bot_b_name: str,
    history_a: list[dict[str, Any]],
    history_b: list[dict[str, Any]],
    facts: list[dict[str, Any]],
) -> float:
    """Blend LLM self-assessment with measurable data coverage signals."""
    llm = max(0.0, min(1.0, llm_confidence))

    match_count = len(history_a) + len(history_b)
    fact_count = len(facts)
    coverage = min(1.0, 0.35 + match_count * 0.025 + fact_count * 0.008)

    rate_a = _win_rate(history_a)
    rate_b = _win_rate(history_b)
    picked_a = winner_name.lower() == bot_a_name.lower()
    if rate_a is not None and rate_b is not None:
        record_edge = (rate_a - rate_b) if picked_a else (rate_b - rate_a)
    elif rate_a is not None:
        record_edge = rate_a - 0.5 if picked_a else 0.5 - rate_a
    elif rate_b is not None:
        record_edge = 0.5 - rate_b if picked_a else rate_b - 0.5
    else:
        record_edge = 0.0
    record_signal = 0.48 + min(0.42, max(-0.12, record_edge * 0.55))

    if match_count < 3:
        llm = min(llm, 0.54)
    if fact_count < 6:
        llm = min(llm, 0.61)

    blended = llm * 0.62 + coverage * record_signal * 0.38
    return round(max(0.18, min(0.93, blended)), 3)


def _win_rate(history: list[dict[str, Any]]) -> float | None:
    decided = [row for row in history if row.get("won") is not None]
    if not decided:
        return None
    wins = sum(1 for row in decided if row.get("won") is True)
    return wins / len(decided)


def _source_name(url: str | None) -> str | None:
    if not url:
        return None
    if "reddit.com" in url:
        return "Reddit"
    if "fandom.com" in url or "battlebots" in url.lower():
        return "BattleBots Wiki"
    return "Web source"


def _match_source_name(url: str | None) -> str:
    if url and "reddit.com" in url:
        return "Reddit"
    if url and ("fandom.com" in url or "battlebots" in url.lower()):
        return "BattleBots Wiki"
    return "Match recap"
