"""SQLite schema definitions for BattleBots data.

Schema is defined as raw SQL DDL strings so the source of truth lives in one
place. `initialize_database()` (in `database.py`) applies these on first run.
"""

from __future__ import annotations

# Use IF NOT EXISTS everywhere so the init function is safely re-runnable.
SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS bots (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT    NOT NULL UNIQUE,
        weight_class    TEXT,
        weapon_type     TEXT,
        weapon_description TEXT,
        team_name       TEXT,
        country         TEXT,
        image_url       TEXT,
        description     TEXT,
        source_url      TEXT,
        scraped_at      TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_bots_name ON bots(name);
    """,
    """
    CREATE TABLE IF NOT EXISTS matches (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_a_id        INTEGER NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
        bot_b_id        INTEGER NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
        winner_id       INTEGER          REFERENCES bots(id) ON DELETE SET NULL,
        method          TEXT,
        season          TEXT,
        episode         TEXT,
        round           TEXT,
        source_url      TEXT,
        scraped_at      TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE(bot_a_id, bot_b_id, season, round, episode)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_matches_bot_a ON matches(bot_a_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_matches_bot_b ON matches(bot_b_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_matches_winner ON matches(winner_id);
    """,
    """
    CREATE TABLE IF NOT EXISTS sentiment (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id          INTEGER NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
        source          TEXT    NOT NULL,
        positive_count  INTEGER NOT NULL DEFAULT 0,
        negative_count  INTEGER NOT NULL DEFAULT 0,
        neutral_count   INTEGER NOT NULL DEFAULT 0,
        sample_quotes   TEXT    NOT NULL DEFAULT '[]',
        scraped_at      TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE(bot_id, source)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_sentiment_bot ON sentiment(bot_id);
    """,
    """
    CREATE TABLE IF NOT EXISTS sentiment_chunks (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id          INTEGER NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
        source          TEXT    NOT NULL DEFAULT 'reddit',
        external_id     TEXT    NOT NULL,
        chunk_type      TEXT    NOT NULL,
        text            TEXT    NOT NULL,
        url             TEXT,
        metadata_json   TEXT,
        embedding_json  TEXT    NOT NULL,
        scraped_at      TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE(bot_id, source, external_id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_sentiment_chunks_bot ON sentiment_chunks(bot_id);
    """,
    """
    CREATE TABLE IF NOT EXISTS predictions (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_a_id            INTEGER NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
        bot_b_id            INTEGER NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
        winner_prediction   INTEGER          REFERENCES bots(id) ON DELETE SET NULL,
        confidence          REAL,
        scouting_report     TEXT    NOT NULL,
        model               TEXT,
        created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE(bot_a_id, bot_b_id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at DESC);
    """,
)
