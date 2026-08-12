"""Streaming log endpoint backed by the in-memory ring buffer.

The frontend polls this every few seconds with `?after=<last_id>` so we only
ever ship deltas. Polling is simpler than SSE/websockets and good enough for
the volume we produce (a few dozen lines per prediction).
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from ..logging_setup import memory_log_handler
from .schemas import LogEntry, LogStreamResponse

router = APIRouter(tags=["logs"])


@router.get("/logs", response_model=LogStreamResponse)
def get_logs(
    after: int = Query(default=0, ge=0, description="Return entries with id > after"),
    limit: int = Query(default=200, ge=1, le=500),
) -> LogStreamResponse:
    """Return log lines newer than `after`, oldest first."""
    snapshot = memory_log_handler.snapshot(after_id=after, limit=limit)
    entries = [LogEntry(**entry) for entry in snapshot]
    cursor = entries[-1].id if entries else after
    return LogStreamResponse(entries=entries, cursor=cursor)
