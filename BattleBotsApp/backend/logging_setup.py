"""Shared logging configuration.

Call `configure_logging()` once at the top of any entry point script.

In addition to the standard stdout handler we install an in-memory ring-buffer
handler so the API can serve recent log records to the frontend dashboard via
`GET /logs`. The buffer is bounded (default 500 records) and lives on the
module so multiple workers/requests share the same view.
"""

from __future__ import annotations

import logging
import sys
from collections import deque
from threading import Lock
from typing import Any, Deque

from .config import settings

_CONFIGURED = False
_MAX_LOG_RECORDS = 500


class MemoryLogHandler(logging.Handler):
    """Logging handler that keeps the last N records in a thread-safe deque.

    Records are emitted as plain dicts so we don't keep a reference to the
    raw `LogRecord` (which can hold tracebacks and module references that
    inflate memory over time).
    """

    def __init__(self, capacity: int = _MAX_LOG_RECORDS) -> None:
        super().__init__()
        self._buffer: Deque[dict[str, Any]] = deque(maxlen=capacity)
        self._lock = Lock()
        # Monotonic id used by the frontend for cursor-style polling — we want
        # "give me everything after id X" semantics so we never re-render the
        # same line twice.
        self._next_id = 1

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 — never let logging crash the app
            message = record.msg if isinstance(record.msg, str) else repr(record.msg)

        entry = {
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "timestamp": self.formatTime(record),
        }
        with self._lock:
            entry["id"] = self._next_id
            self._next_id += 1
            self._buffer.append(entry)

    @staticmethod
    def formatTime(record: logging.LogRecord) -> str:
        # ISO-ish formatting matches what `configure_logging` shows on stdout.
        import time

        ct = time.localtime(record.created)
        return time.strftime("%Y-%m-%d %H:%M:%S", ct)

    def snapshot(self, *, after_id: int = 0, limit: int = 200) -> list[dict[str, Any]]:
        """Return entries with `id > after_id`, oldest first, capped at `limit`."""
        with self._lock:
            filtered = [entry for entry in self._buffer if entry["id"] > after_id]
        if len(filtered) > limit:
            filtered = filtered[-limit:]
        return filtered

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()
            self._next_id = 1


# Singleton — initialized inside `configure_logging` so we can reuse it.
memory_log_handler = MemoryLogHandler()


def configure_logging() -> None:
    """Idempotently configure root logging based on settings.log_level."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # Memory handler doesn't need a custom formatter — we build the dict
    # ourselves in `emit`. We still set a level filter so DEBUG noise doesn't
    # crowd the UI.
    memory_log_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    # Remove pre-existing handlers added by libraries to keep output clean.
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(stdout_handler)
    root.addHandler(memory_log_handler)

    # Tame chatty third-party loggers.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    _CONFIGURED = True
