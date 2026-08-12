"""Predict who wins a hypothetical BattleBots matchup.

Steps for `predict(bot_a_id, bot_b_id)`:

1. Look for a cached prediction in the `predictions` table. Return it if found
   (unless `force_refresh=True`).
2. Pull both bots' profile rows, match histories, and sentiment from SQLite.
3. Annotate each history row with `opponent_name` + `won` (relative to the bot
   being analyzed) so the LLM doesn't have to figure that out from raw ids.
4. Build the prompt, call the LLM, parse the response.
5. Cache the new prediction and return it.

The response includes a `sources` block describing exactly what data fed the
LLM, so the UI can show a transparent audit trail.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import asdict
from typing import Any

from .api.sentiment_helpers import sentiment_item_from_row
from .ai import LLMClient, LLMError, ScoutingReport
from .ai.evidence import build_evidence_catalog, refine_confidence
from .ai.prompts import SYSTEM_PROMPT, build_prediction_prompt
from .ai.rag import build_matchup_query, retrieve_sentiment_chunks
from .db import Database
from .db.repositories import (
    BotRepository,
    MatchRepository,
    PredictionRepository,
    SentimentRepository,
)

logger = logging.getLogger(__name__)


def predict(
    bot_a_id: int,
    bot_b_id: int,
    *,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Return a scouting-report dict for the given matchup."""
    if bot_a_id == bot_b_id:
        raise ValueError("bot_a_id and bot_b_id must be different.")

    with Database() as conn:
        if not force_refresh:
            cached = PredictionRepository(conn).get_for_pair(bot_a_id, bot_b_id)
            if cached:
                logger.info(
                    "Cache hit: prediction id=%d for %d vs %d",
                    cached["id"],
                    bot_a_id,
                    bot_b_id,
                )
                return _hydrate_cached(conn, cached)

        logger.info("Building prediction for bots %d vs %d", bot_a_id, bot_b_id)
        bot_a = _require_bot(conn, bot_a_id)
        bot_b = _require_bot(conn, bot_b_id)

        history_a = _build_history(conn, bot_a_id)
        history_b = _build_history(conn, bot_b_id)

        sentiment_a = SentimentRepository(conn).list_for_bot(bot_a_id)
        sentiment_b = SentimentRepository(conn).list_for_bot(bot_b_id)

        rag_query = build_matchup_query(bot_a["name"], bot_b["name"])
        rag_a = retrieve_sentiment_chunks(
            conn, bot_id=bot_a_id, query=rag_query
        )
        rag_b = retrieve_sentiment_chunks(
            conn, bot_id=bot_b_id, query=rag_query
        )

        evidence_catalog = build_evidence_catalog(
            bot_a=dict(bot_a),
            bot_b=dict(bot_b),
            history_a=history_a,
            history_b=history_b,
            sentiment_a=sentiment_a,
            sentiment_b=sentiment_b,
            rag_a=rag_a,
            rag_b=rag_b,
        )

        logger.info(
            "Sources for %s vs %s: %d/%d matches, %d/%d sentiment rows, "
            "%d/%d RAG chunks, %d facts",
            bot_a["name"],
            bot_b["name"],
            len(history_a),
            len(history_b),
            len(sentiment_a),
            len(sentiment_b),
            len(rag_a),
            len(rag_b),
            len(evidence_catalog),
        )

        prompt = build_prediction_prompt(
            bot_a=dict(bot_a),
            bot_b=dict(bot_b),
            history_a=history_a,
            history_b=history_b,
            sentiment_a=sentiment_a,
            sentiment_b=sentiment_b,
            evidence_catalog=evidence_catalog,
        )

        client = LLMClient()
        logger.info("Calling LLM provider=%s model=%s", client.provider, client.model)

        def _adjust_confidence(llm_conf: float, winner: str) -> float:
            return refine_confidence(
                llm_conf,
                winner_name=winner,
                bot_a_name=bot_a["name"],
                bot_b_name=bot_b["name"],
                history_a=history_a,
                history_b=history_b,
                facts=evidence_catalog,
            )

        try:
            report = client.generate_scouting_report(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
                bot_a_name=bot_a["name"],
                bot_b_name=bot_b["name"],
                refine_confidence=_adjust_confidence,
            )
        except LLMError as err:
            logger.error("LLM call failed for %d vs %d: %s", bot_a_id, bot_b_id, err)
            raise

        logger.info(
            "LLM picked '%s' with confidence %.2f (method=%s)",
            report.winner,
            report.confidence,
            report.method_prediction,
        )

        winner_id = _resolve_winner_id(report.winner, bot_a, bot_b)
        prediction_row_id = PredictionRepository(conn).upsert(
            bot_a_id=bot_a_id,
            bot_b_id=bot_b_id,
            winner_prediction=winner_id,
            confidence=report.confidence,
            scouting_report=report.raw_response,
            model=report.model,
        )

        sources = _build_sources(
            bot_a=bot_a,
            bot_b=bot_b,
            history_a=history_a,
            history_b=history_b,
            sentiment_a=sentiment_a,
            sentiment_b=sentiment_b,
        )

        return _format_response(
            prediction_id=prediction_row_id,
            bot_a=bot_a,
            bot_b=bot_b,
            report=report,
            winner_id=winner_id,
            cached=False,
            sources=sources,
            evidence_catalog=evidence_catalog,
        )


def get_prediction(prediction_id: int) -> dict[str, Any]:
    """Load a stored prediction by id with fresh sources + evidence catalog."""
    with Database() as conn:
        cached = PredictionRepository(conn).get_by_id(prediction_id)
        if cached is None:
            raise ValueError(f"Unknown prediction id: {prediction_id}")
        return _hydrate_cached(conn, cached)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _require_bot(conn: sqlite3.Connection, bot_id: int) -> sqlite3.Row:
    row = BotRepository(conn).get_by_id(bot_id)
    if row is None:
        raise ValueError(f"Unknown bot id: {bot_id}")
    return row


def _build_history(
    conn: sqlite3.Connection, bot_id: int
) -> list[dict[str, Any]]:
    """Return enriched match history relative to `bot_id`.

    Each row has `opponent_name` and `won` set so the LLM doesn't have to
    cross-reference ids.
    """
    rows = MatchRepository(conn).list_for_bot(bot_id)
    bot_repo = BotRepository(conn)

    enriched = []
    for row in rows:
        opponent_id = (
            row["bot_b_id"] if row["bot_a_id"] == bot_id else row["bot_a_id"]
        )
        opponent = bot_repo.get_by_id(opponent_id)
        opponent_name = opponent["name"] if opponent else None

        won: bool | None
        if row["winner_id"] is None:
            won = None
        else:
            won = bool(row["winner_id"] == bot_id)

        enriched.append(
            {
                "id": int(row["id"]),
                "opponent_id": opponent_id,
                "opponent_name": opponent_name,
                "won": won,
                "method": row["method"],
                "season": row["season"],
                "episode": row["episode"],
                "round": row["round"],
                "source_url": row["source_url"],
            }
        )
    return enriched


def _resolve_winner_id(
    winner_name: str, bot_a: sqlite3.Row, bot_b: sqlite3.Row
) -> int | None:
    if not winner_name:
        return None
    if winner_name.lower() == bot_a["name"].lower():
        return int(bot_a["id"])
    if winner_name.lower() == bot_b["name"].lower():
        return int(bot_b["id"])
    return None


def _record(history: list[dict[str, Any]]) -> dict[str, int]:
    """Win/loss/draw tally for a bot's history list."""
    wins = sum(1 for row in history if row.get("won") is True)
    losses = sum(1 for row in history if row.get("won") is False)
    draws = sum(1 for row in history if row.get("won") is None)
    return {"wins": wins, "losses": losses, "draws": draws}


def _build_sources(
    *,
    bot_a: sqlite3.Row,
    bot_b: sqlite3.Row,
    history_a: list[dict[str, Any]],
    history_b: list[dict[str, Any]],
    sentiment_a: list[dict[str, Any]],
    sentiment_b: list[dict[str, Any]],
) -> dict[str, Any]:
    """Structured snapshot of the inputs that fed the LLM.

    Shapes match the frontend `PredictionSources` interface so the UI can
    render an evidence panel directly from this dict.
    """
    return {
        "bot_a": {
            "profile": _profile_for_sources(bot_a),
            "record": _record(history_a),
            "matches": history_a,
            "sentiment": [
                sentiment_item_from_row(row).model_dump() for row in sentiment_a
            ],
        },
        "bot_b": {
            "profile": _profile_for_sources(bot_b),
            "record": _record(history_b),
            "matches": history_b,
            "sentiment": [
                sentiment_item_from_row(row).model_dump() for row in sentiment_b
            ],
        },
    }


def _profile_for_sources(bot: sqlite3.Row) -> dict[str, Any]:
    """Just the fields we want to show in the evidence panel."""
    return {
        "id": int(bot["id"]),
        "name": bot["name"],
        "weight_class": bot["weight_class"],
        "weapon_type": bot["weapon_type"],
        "weapon_description": bot["weapon_description"],
        "team_name": bot["team_name"],
        "country": bot["country"],
        "image_url": bot["image_url"],
        "source_url": bot["source_url"],
    }


def _format_response(
    *,
    prediction_id: int,
    bot_a: sqlite3.Row,
    bot_b: sqlite3.Row,
    report: ScoutingReport,
    winner_id: int | None,
    cached: bool,
    sources: dict[str, Any],
    evidence_catalog: list[dict[str, Any]],
) -> dict[str, Any]:
    """Public-facing JSON shape consumed by the API + frontend."""
    body = asdict(report)
    body.pop("raw_response", None)
    fact_citations = [
        _fact_citation_to_dict(c) for c in body.pop("fact_citations", [])
    ]
    return {
        "prediction_id": prediction_id,
        "bot_a": {"id": int(bot_a["id"]), "name": bot_a["name"]},
        "bot_b": {"id": int(bot_b["id"]), "name": bot_b["name"]},
        "winner_id": winner_id,
        "cached": cached,
        "sources": sources,
        "evidence_catalog": evidence_catalog,
        "fact_citations": fact_citations,
        **body,
    }


def _hydrate_cached(
    conn: sqlite3.Connection, cached: sqlite3.Row
) -> dict[str, Any]:
    """Rebuild a response dict from a cached `predictions` row.

    We re-derive the sources from the current DB (not the moment of
    prediction) — that's actually desirable: if you re-scrape and run the
    same matchup, you'll see the freshest evidence.
    """
    bot_repo = BotRepository(conn)
    bot_a = bot_repo.get_by_id(int(cached["bot_a_id"]))
    bot_b = bot_repo.get_by_id(int(cached["bot_b_id"]))
    if bot_a is None or bot_b is None:
        # The bots were deleted under us; ignore the cache.
        raise ValueError("Cached prediction references missing bot rows.")

    # Re-parse the stored raw response so we return rich fields.
    try:
        client_payload = LLMClient._extract_json(cached["scouting_report"])
    except LLMError:
        client_payload = {}

    report = ScoutingReport(
        winner=str(client_payload.get("winner") or ""),
        confidence=round(float(cached["confidence"] or 0.0), 3),
        method_prediction=str(client_payload.get("method_prediction") or "UNCLEAR"),
        key_factors=list(client_payload.get("key_factors") or []),
        weapon_matchup=str(client_payload.get("weapon_matchup") or ""),
        narrative=str(client_payload.get("narrative") or ""),
        x_factor=str(client_payload.get("x_factor") or ""),
        raw_response=cached["scouting_report"],
        model=cached["model"] or "",
        reasoning_steps=list(client_payload.get("reasoning_steps") or []),
        evidence_citations=list(client_payload.get("evidence_citations") or []),
        fact_citations=_parse_fact_citations(client_payload.get("fact_citations")),
    )

    history_a = _build_history(conn, int(bot_a["id"]))
    history_b = _build_history(conn, int(bot_b["id"]))
    sentiment_a = SentimentRepository(conn).list_for_bot(int(bot_a["id"]))
    sentiment_b = SentimentRepository(conn).list_for_bot(int(bot_b["id"]))
    evidence_catalog = build_evidence_catalog(
        bot_a=dict(bot_a),
        bot_b=dict(bot_b),
        history_a=history_a,
        history_b=history_b,
        sentiment_a=sentiment_a,
        sentiment_b=sentiment_b,
    )
    sources = _build_sources(
        bot_a=bot_a,
        bot_b=bot_b,
        history_a=history_a,
        history_b=history_b,
        sentiment_a=sentiment_a,
        sentiment_b=sentiment_b,
    )

    return _format_response(
        prediction_id=int(cached["id"]),
        bot_a=bot_a,
        bot_b=bot_b,
        report=report,
        winner_id=cached["winner_prediction"],
        cached=True,
        sources=sources,
        evidence_catalog=evidence_catalog,
    )


def _parse_fact_citations(raw: Any) -> list:
    from .ai.llm_client import FactCitation, _coerce_fact_citations

    return _coerce_fact_citations(raw)


def _fact_citation_to_dict(citation: Any) -> dict[str, str]:
    if isinstance(citation, dict):
        return {
            "fact_id": str(citation.get("fact_id") or citation.get("id") or ""),
            "claim": str(citation.get("claim") or ""),
            "supports": str(citation.get("supports") or "neutral"),
        }
    return {
        "fact_id": citation.fact_id,
        "claim": citation.claim,
        "supports": citation.supports,
    }
