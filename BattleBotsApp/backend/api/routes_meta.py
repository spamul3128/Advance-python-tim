"""Meta endpoints: health check and a stats snapshot for the architecture diagram.

`/stats` powers the animated diagram on the frontend — it just needs row counts
per table so the React side can show "X bots scraped, Y matches indexed, etc."
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import settings
from ..db import Database
from ..db.repositories import (
    BotRepository,
    MatchRepository,
    PredictionRepository,
)

router = APIRouter(tags=["meta"])


class HealthResponse(BaseModel):
    status: str
    timestamp: str


class StatsResponse(BaseModel):
    bots: int
    matches: int
    predictions: int
    sentiment_rows: int
    llm_provider: str
    llm_model: str


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    with Database() as conn:
        bots = BotRepository(conn).count()
        matches = MatchRepository(conn).count()
        prediction_rows = conn.execute(
            "SELECT COUNT(*) AS c FROM predictions"
        ).fetchone()
        sentiment_rows = conn.execute(
            "SELECT COUNT(*) AS c FROM sentiment"
        ).fetchone()

    model = (
        settings.openai_model
        if settings.llm_provider == "openai"
        else settings.anthropic_model
    )
    return StatsResponse(
        bots=bots,
        matches=matches,
        predictions=int(prediction_rows["c"]) if prediction_rows else 0,
        sentiment_rows=int(sentiment_rows["c"]) if sentiment_rows else 0,
        llm_provider=settings.llm_provider,
        llm_model=model,
    )
