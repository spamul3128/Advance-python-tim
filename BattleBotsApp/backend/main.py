"""FastAPI application entrypoint.

Run via uv::

    uv run uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_bots import router as bots_router
from .api.routes_explorer import router as explorer_router
from .api.routes_logs import router as logs_router
from .api.routes_meta import router as meta_router
from .api.routes_predictions import router as predictions_router
from .db import initialize_database
from .logging_setup import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hook: configure logging + ensure DB schema exists."""
    configure_logging()
    initialize_database()
    yield


app = FastAPI(
    title="BattleBots AI Fight Predictor",
    version="0.1.0",
    description="Scrapes BattleBots data via Bright Data and generates AI scouting reports.",
    lifespan=lifespan,
)

# Local development: the React dev server runs on :5173.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta_router)
app.include_router(logs_router)
app.include_router(bots_router)
app.include_router(predictions_router)
app.include_router(explorer_router)
