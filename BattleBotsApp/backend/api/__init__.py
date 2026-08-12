"""FastAPI route modules."""

from .schemas import (
    BotDetailResponse,
    BotSummary,
    PredictionRequest,
    PredictionResponse,
)

__all__ = [
    "BotSummary",
    "BotDetailResponse",
    "PredictionRequest",
    "PredictionResponse",
]
