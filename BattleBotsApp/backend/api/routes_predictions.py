"""Prediction endpoints: POST /predict + GET /predictions."""

from __future__ import annotations

import logging
import sqlite3

from fastapi import APIRouter, HTTPException, Query

from ..ai import LLMError
from ..db import Database
from ..db.repositories import BotRepository, PredictionRepository
from ..predictor import get_prediction, predict
from .schemas import (
    BotReference,
    PredictionListItem,
    PredictionRequest,
    PredictionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["predictions"])


@router.post("/predict", response_model=PredictionResponse)
def create_prediction(body: PredictionRequest) -> PredictionResponse:
    """Generate (or fetch cached) scouting report for a bot pair."""
    if body.bot_a_id == body.bot_b_id:
        raise HTTPException(status_code=400, detail="bot_a_id and bot_b_id must differ.")
    try:
        result = predict(
            body.bot_a_id,
            body.bot_b_id,
            force_refresh=body.force_refresh,
        )
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except LLMError as err:
        logger.exception("LLM failure")
        raise HTTPException(status_code=502, detail=f"LLM call failed: {err}") from err
    return PredictionResponse(**result)


@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
def get_prediction_by_id(prediction_id: int) -> PredictionResponse:
    """Return the full scouting report for a stored prediction."""
    try:
        result = get_prediction(prediction_id)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    return PredictionResponse(**result)


@router.get("/predictions", response_model=list[PredictionListItem])
def list_predictions(limit: int = Query(default=20, ge=1, le=100)) -> list[PredictionListItem]:
    """Recent predictions for a feed/history view."""
    with Database() as conn:
        rows = PredictionRepository(conn).list_recent(limit=limit)
        return [_row_to_list_item(conn, row) for row in rows]


def _row_to_list_item(conn: sqlite3.Connection, row: sqlite3.Row) -> PredictionListItem:
    bot_repo = BotRepository(conn)
    a = bot_repo.get_by_id(int(row["bot_a_id"]))
    b = bot_repo.get_by_id(int(row["bot_b_id"]))
    winner = bot_repo.get_by_id(int(row["winner_prediction"])) if row["winner_prediction"] else None
    return PredictionListItem(
        id=int(row["id"]),
        bot_a=BotReference(id=int(a["id"]), name=a["name"]) if a else BotReference(id=0, name="?"),
        bot_b=BotReference(id=int(b["id"]), name=b["name"]) if b else BotReference(id=0, name="?"),
        winner_id=int(row["winner_prediction"]) if row["winner_prediction"] else None,
        winner_name=winner["name"] if winner else None,
        confidence=float(row["confidence"]) if row["confidence"] is not None else None,
        created_at=row["created_at"],
        model=row["model"],
    )
