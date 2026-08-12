"""Pydantic response models for the API.

Centralized so the FastAPI routes stay focused on orchestration and the
frontend can generate types from the OpenAPI schema later.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field


class BotSummary(BaseModel):
    """Lightweight bot record returned by the listing endpoint."""

    id: int
    name: str
    weight_class: str | None = None
    weapon_type: str | None = None
    team_name: str | None = None
    country: str | None = None
    image_url: str | None = None


class MatchHistoryItem(BaseModel):
    # `id` and `opponent_id` are optional because the predictor's enriched
    # history list doesn't carry the raw row ids — it only knows opponent name
    # and outcome relative to the bot being analyzed.
    id: int | None = None
    opponent_id: int | None = None
    opponent_name: str | None = None
    won: bool | None = None
    method: str | None = None
    season: str | None = None
    round: str | None = None
    episode: str | None = None
    source_url: str | None = None


class EvidenceFact(BaseModel):
    """A single numbered fact from the scraped evidence catalog."""

    id: str
    category: str
    bot: str
    label: str
    detail: str
    source_url: str | None = None
    source_name: str | None = None


class FactCitation(BaseModel):
    """LLM claim tied to a catalog fact ID."""

    fact_id: str
    claim: str
    supports: str = "neutral"


class SentimentPost(BaseModel):
    """A single scraped fan post (Reddit thread, tweet, etc.)."""

    id: str | None = None
    title: str
    body: str | None = None
    url: str | None = None
    score: int | None = None
    num_comments: int | None = None
    created_at: str | None = None
    subreddit: str | None = None
    sentiment: str | None = None
    text: str = ""


class SentimentItem(BaseModel):
    source: str
    positive_count: int
    negative_count: int
    neutral_count: int
    posts: list[SentimentPost] = Field(default_factory=list)
    sample_quotes: list[str] = Field(default_factory=list)


class BotDetailResponse(BotSummary):
    description: str | None = None
    weapon_description: str | None = None
    matches: list[MatchHistoryItem] = Field(default_factory=list)
    sentiment: list[SentimentItem] = Field(default_factory=list)


class BotReference(BaseModel):
    id: int
    name: str


class PredictionRequest(BaseModel):
    bot_a_id: int
    bot_b_id: int
    force_refresh: bool = False


class BotSourceProfile(BaseModel):
    """Subset of the bot row exposed in a prediction's `sources` block."""

    id: int
    name: str
    weight_class: str | None = None
    weapon_type: str | None = None
    weapon_description: str | None = None
    team_name: str | None = None
    country: str | None = None
    image_url: str | None = None
    source_url: str | None = None


class BotSourceRecord(BaseModel):
    wins: int
    losses: int
    draws: int


class BotSourceBundle(BaseModel):
    """Everything the predictor knew about one of the bots in the matchup."""

    profile: BotSourceProfile
    record: BotSourceRecord
    matches: list[MatchHistoryItem] = Field(default_factory=list)
    sentiment: list[SentimentItem] = Field(default_factory=list)


class PredictionSources(BaseModel):
    """Audit trail of the data that fed the LLM."""

    bot_a: BotSourceBundle
    bot_b: BotSourceBundle


class PredictionResponse(BaseModel):
    prediction_id: int
    bot_a: BotReference
    bot_b: BotReference
    winner_id: int | None
    winner: str
    confidence: float
    method_prediction: str
    key_factors: list[str]
    weapon_matchup: str
    narrative: str
    x_factor: str
    reasoning_steps: list[str] = Field(default_factory=list)
    evidence_citations: list[str] = Field(default_factory=list)
    fact_citations: list[FactCitation] = Field(default_factory=list)
    evidence_catalog: list[EvidenceFact] = Field(default_factory=list)
    model: str
    cached: bool
    sources: PredictionSources


class PredictionListItem(BaseModel):
    id: int
    bot_a: BotReference
    bot_b: BotReference
    winner_id: int | None
    winner_name: str | None
    confidence: float | None
    created_at: str
    model: str | None


# ---------------------------------------------------------------------------
# Data explorer
# ---------------------------------------------------------------------------
# Generic paginated envelope — all explorer endpoints share the same shape so
# the frontend can render a single table component for every table.
T = TypeVar("T")


class ExplorerPage(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]


class ExplorerBotRow(BaseModel):
    id: int
    name: str
    weight_class: str | None = None
    weapon_type: str | None = None
    team_name: str | None = None
    country: str | None = None
    source_url: str | None = None
    scraped_at: str | None = None


class ExplorerMatchRow(BaseModel):
    id: int
    bot_a_id: int | None = None
    bot_a_name: str | None = None
    bot_b_id: int | None = None
    bot_b_name: str | None = None
    winner_id: int | None = None
    winner_name: str | None = None
    method: str | None = None
    season: str | None = None
    episode: str | None = None
    round: str | None = None
    source_url: str | None = None
    scraped_at: str | None = None


class ExplorerSentimentRow(BaseModel):
    id: int
    bot_id: int | None = None
    bot_name: str | None = None
    source: str
    positive_count: int
    negative_count: int
    neutral_count: int
    posts: list[SentimentPost] = Field(default_factory=list)
    sample_quotes: list[str] = Field(default_factory=list)
    scraped_at: str | None = None


class ExplorerPredictionRow(BaseModel):
    id: int
    bot_a_id: int | None = None
    bot_a_name: str | None = None
    bot_b_id: int | None = None
    bot_b_name: str | None = None
    winner_id: int | None = None
    winner_name: str | None = None
    confidence: float | None = None
    model: str | None = None
    created_at: str


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------
class LogEntry(BaseModel):
    id: int
    timestamp: str
    level: str
    logger: str
    message: str


class LogStreamResponse(BaseModel):
    entries: list[LogEntry]
    # `cursor` is the highest id in this batch so the client can poll with
    # `?after=cursor` and only receive new lines.
    cursor: int
