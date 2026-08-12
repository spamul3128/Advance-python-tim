"""Bot listing + bot-detail endpoints."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException

from ..db import Database
from ..db.repositories import BotRepository, MatchRepository, SentimentRepository
from .schemas import BotDetailResponse, BotSummary, MatchHistoryItem
from .sentiment_helpers import sentiment_item_from_row

router = APIRouter(prefix="/bots", tags=["bots"])


@router.get("", response_model=list[BotSummary])
def list_bots() -> list[BotSummary]:
    """Return every bot in the database (sorted by name)."""
    with Database() as conn:
        rows = BotRepository(conn).list_all()
        return [_row_to_summary(row) for row in rows]


@router.get("/{bot_id}", response_model=BotDetailResponse)
def get_bot(bot_id: int) -> BotDetailResponse:
    """Return a single bot with full match history + sentiment."""
    with Database() as conn:
        bot_repo = BotRepository(conn)
        match_repo = MatchRepository(conn)
        sentiment_repo = SentimentRepository(conn)

        row = bot_repo.get_by_id(bot_id)
        if row is None:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found.")

        match_rows = match_repo.list_for_bot(bot_id)
        history = [_build_history_item(conn, bot_id, m) for m in match_rows]

        sentiment_rows = sentiment_repo.list_for_bot(bot_id)
        sentiment = [sentiment_item_from_row(row) for row in sentiment_rows]

        return BotDetailResponse(
            **_row_to_summary(row).model_dump(),
            description=row["description"],
            weapon_description=row["weapon_description"],
            matches=history,
            sentiment=sentiment,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _row_to_summary(row: sqlite3.Row) -> BotSummary:
    return BotSummary(
        id=int(row["id"]),
        name=row["name"],
        weight_class=row["weight_class"],
        weapon_type=row["weapon_type"],
        team_name=row["team_name"],
        country=row["country"],
        image_url=row["image_url"],
    )


def _build_history_item(
    conn: sqlite3.Connection, bot_id: int, m: sqlite3.Row
) -> MatchHistoryItem:
    opponent_id = m["bot_b_id"] if m["bot_a_id"] == bot_id else m["bot_a_id"]
    opponent = BotRepository(conn).get_by_id(opponent_id)
    won: bool | None
    if m["winner_id"] is None:
        won = None
    else:
        won = bool(m["winner_id"] == bot_id)
    return MatchHistoryItem(
        id=int(m["id"]),
        opponent_id=opponent_id,
        opponent_name=opponent["name"] if opponent else None,
        won=won,
        method=m["method"],
        season=m["season"],
        round=m["round"],
        episode=m["episode"],
    )
