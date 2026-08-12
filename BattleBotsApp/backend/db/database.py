"""SQLite connection management and schema initialization.

We intentionally use the stdlib `sqlite3` module — the plan calls for SQLite,
no ORM, and the data volume here is trivially small.

Connections are created lazily and *not* shared across threads. Each request
or scraper invocation should grab its own connection via `get_connection()`
or use the `Database` context manager.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from ..config import settings
from .schema import SCHEMA_STATEMENTS

logger = logging.getLogger(__name__)


def _ensure_parent_dir(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a new SQLite connection with sane defaults.

    - `row_factory` set to sqlite3.Row so callers can index by column name.
    - Foreign keys enabled (off by default in SQLite).
    - WAL journal mode for better concurrent read performance.
    """
    path = db_path or settings.database_full_path
    _ensure_parent_dir(path)
    conn = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def initialize_database(db_path: Path | None = None) -> None:
    """Create all tables and indexes if they don't exist."""
    path = db_path or settings.database_full_path
    logger.info("Initializing database at %s", path)
    conn = get_connection(path)
    try:
        with conn:
            for stmt in SCHEMA_STATEMENTS:
                conn.execute(stmt)
    finally:
        conn.close()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Context manager that wraps statements in an explicit transaction.

    Because we open connections with `isolation_level=None` (autocommit),
    we manage transactions manually with BEGIN/COMMIT/ROLLBACK so failures
    cleanly roll back partial writes.
    """
    conn.execute("BEGIN;")
    try:
        yield conn
    except Exception:
        conn.execute("ROLLBACK;")
        raise
    else:
        conn.execute("COMMIT;")


class Database:
    """Convenience context manager for short-lived DB sessions.

    Usage::

        with Database() as db:
            db.execute("INSERT INTO ...", (...))
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Connection:
        self._conn = get_connection(self._db_path)
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
