"""Data explorer endpoints.

These power the UI's data-browser panel: read-only, paginated views over
every table that's interesting to a human. Each row is joined with bot names
where applicable so the frontend doesn't need to do client-side lookups.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from fastapi import APIRouter, Query

from ..db import Database
from .schemas import (
    ExplorerBotRow,
    ExplorerMatchRow,
    ExplorerPage,
    ExplorerPredictionRow,
    ExplorerSentimentRow,
)
from .sentiment_helpers import explorer_sentiment_row_from_dict

router = APIRouter(prefix="/explorer", tags=["explorer"])


@router.get("/bots", response_model=ExplorerPage[ExplorerBotRow])
def explorer_bots(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ExplorerPage[ExplorerBotRow]:
    with Database() as conn:
        total = _count(conn, "SELECT COUNT(*) AS c FROM bots")
        rows = conn.execute(
            """
            SELECT id, name, weight_class, weapon_type, team_name, country,
                   source_url, scraped_at
            FROM bots
            ORDER BY name ASC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        items = [ExplorerBotRow(**dict(r)) for r in rows]
    return ExplorerPage(total=total, limit=limit, offset=offset, items=items)


@router.get("/matches", response_model=ExplorerPage[ExplorerMatchRow])
def explorer_matches(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    bot_id: int | None = Query(default=None),
) -> ExplorerPage[ExplorerMatchRow]:
    """Paginated match log. Optionally filter by `bot_id` (either competitor)."""
    where, params = "", []
    if bot_id is not None:
        where = "WHERE m.bot_a_id = ? OR m.bot_b_id = ?"
        params = [bot_id, bot_id]

    with Database() as conn:
        total = _count(
            conn,
            f"SELECT COUNT(*) AS c FROM matches m {where}",
            tuple(params),
        )
        rows = conn.execute(
            f"""
            SELECT
                m.id,
                m.bot_a_id, ba.name AS bot_a_name,
                m.bot_b_id, bb.name AS bot_b_name,
                m.winner_id, bw.name AS winner_name,
                m.method, m.season, m.episode, m.round,
                m.source_url, m.scraped_at
            FROM matches m
            LEFT JOIN bots ba ON ba.id = m.bot_a_id
            LEFT JOIN bots bb ON bb.id = m.bot_b_id
            LEFT JOIN bots bw ON bw.id = m.winner_id
            {where}
            ORDER BY m.scraped_at DESC, m.id DESC
            LIMIT ? OFFSET ?
            """,
            (*params, limit, offset),
        ).fetchall()
        items = [ExplorerMatchRow(**dict(r)) for r in rows]
    return ExplorerPage(total=total, limit=limit, offset=offset, items=items)


@router.get("/sentiment", response_model=ExplorerPage[ExplorerSentimentRow])
def explorer_sentiment(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ExplorerPage[ExplorerSentimentRow]:
    with Database() as conn:
        total = _count(conn, "SELECT COUNT(*) AS c FROM sentiment")
        rows = conn.execute(
            """
            SELECT
                s.id, s.bot_id, b.name AS bot_name,
                s.source, s.positive_count, s.negative_count, s.neutral_count,
                s.sample_quotes, s.scraped_at
            FROM sentiment s
            LEFT JOIN bots b ON b.id = s.bot_id
            ORDER BY s.scraped_at DESC, s.id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        items: list[ExplorerSentimentRow] = []
        for r in rows:
            data = dict(r)
            raw = _safe_json_list(data.get("sample_quotes"))
            data["sample_quotes"] = raw
            items.append(explorer_sentiment_row_from_dict(data))
    return ExplorerPage(total=total, limit=limit, offset=offset, items=items)


@router.get("/predictions", response_model=ExplorerPage[ExplorerPredictionRow])
def explorer_predictions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ExplorerPage[ExplorerPredictionRow]:
    with Database() as conn:
        total = _count(conn, "SELECT COUNT(*) AS c FROM predictions")
        rows = conn.execute(
            """
            SELECT
                p.id, p.bot_a_id, ba.name AS bot_a_name,
                p.bot_b_id, bb.name AS bot_b_name,
                p.winner_prediction AS winner_id, bw.name AS winner_name,
                p.confidence, p.model, p.created_at
            FROM predictions p
            LEFT JOIN bots ba ON ba.id = p.bot_a_id
            LEFT JOIN bots bb ON bb.id = p.bot_b_id
            LEFT JOIN bots bw ON bw.id = p.winner_prediction
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        items = [ExplorerPredictionRow(**dict(r)) for r in rows]
    return ExplorerPage(total=total, limit=limit, offset=offset, items=items)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _count(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> int:
    row = conn.execute(sql, params).fetchone()
    return int(row["c"]) if row else 0


def _safe_json_list(value: Any) -> list[str]:
    """Sentiment rows store quotes as a JSON-encoded list — decode defensively."""
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        decoded = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
    return [str(item) for item in decoded] if isinstance(decoded, list) else []
