"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.db import get_connection, initialize_database


@pytest.fixture()
def tmp_db(tmp_path: Path):
    """Initialize a clean SQLite DB in a tmp dir and yield a connection."""
    db_file = tmp_path / "test.db"
    initialize_database(db_file)
    conn = get_connection(db_file)
    try:
        yield conn
    finally:
        conn.close()
