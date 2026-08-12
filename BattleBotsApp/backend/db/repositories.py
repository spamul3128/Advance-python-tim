"""Data access helpers for the four tables.

Repositories keep SQL out of scraper/business logic and centralize upsert
semantics. Each repository takes a `sqlite3.Connection` so callers control
transaction boundaries.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Iterable

from ..scrapers.parsers.sentiment_parser import normalize_posts


# ---------------------------------------------------------------------------
# Bots
# ---------------------------------------------------------------------------
class BotRepository:
    """CRUD for the `bots` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(self, bot: dict[str, Any]) -> int:
        """Insert or update a bot keyed by `name`. Returns the bot id."""
        cur = self.conn.execute(
            """
            INSERT INTO bots (
                name, weight_class, weapon_type, weapon_description,
                team_name, country, image_url, description, source_url
            )
            VALUES (
                :name, :weight_class, :weapon_type, :weapon_description,
                :team_name, :country, :image_url, :description, :source_url
            )
            ON CONFLICT(name) DO UPDATE SET
                weight_class       = excluded.weight_class,
                weapon_type        = excluded.weapon_type,
                weapon_description = excluded.weapon_description,
                team_name          = excluded.team_name,
                country            = excluded.country,
                image_url          = excluded.image_url,
                description        = excluded.description,
                source_url         = excluded.source_url,
                scraped_at         = datetime('now')
            """,
            {
                "name": bot["name"],
                "weight_class": bot.get("weight_class"),
                "weapon_type": bot.get("weapon_type"),
                "weapon_description": bot.get("weapon_description"),
                "team_name": bot.get("team_name"),
                "country": bot.get("country"),
                "image_url": bot.get("image_url"),
                "description": bot.get("description"),
                "source_url": bot.get("source_url"),
            },
        )
        # cur.lastrowid is unreliable on UPDATE conflict resolution paths.
        row = self.conn.execute(
            "SELECT id FROM bots WHERE name = ?", (bot["name"],)
        ).fetchone()
        return int(row["id"])

    def get_by_id(self, bot_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM bots WHERE id = ?", (bot_id,)
        ).fetchone()

    def get_by_name(self, name: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM bots WHERE name = ?", (name,)
        ).fetchone()

    def list_all(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM bots ORDER BY name ASC"
        ).fetchall()

    def count(self) -> int:
        return int(
            self.conn.execute("SELECT COUNT(*) AS c FROM bots").fetchone()["c"]
        )


# ---------------------------------------------------------------------------
# Matches
# ---------------------------------------------------------------------------
class MatchRepository:
    """CRUD for the `matches` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(self, match: dict[str, Any]) -> int | None:
        """Insert a match, deduping on (bot_a, bot_b, season, round, episode).

        Returns the row id (or None if conflict resolution skipped).
        """
        required = ("bot_a_id", "bot_b_id")
        for field in required:
            if match.get(field) is None:
                raise ValueError(f"match missing required field {field!r}")

        cur = self.conn.execute(
            """
            INSERT INTO matches (
                bot_a_id, bot_b_id, winner_id, method,
                season, episode, round, source_url
            )
            VALUES (
                :bot_a_id, :bot_b_id, :winner_id, :method,
                :season, :episode, :round, :source_url
            )
            ON CONFLICT(bot_a_id, bot_b_id, season, round, episode) DO UPDATE SET
                winner_id  = excluded.winner_id,
                method     = excluded.method,
                source_url = excluded.source_url,
                scraped_at = datetime('now')
            """,
            {
                "bot_a_id": match["bot_a_id"],
                "bot_b_id": match["bot_b_id"],
                "winner_id": match.get("winner_id"),
                "method": match.get("method"),
                "season": match.get("season"),
                "episode": match.get("episode"),
                "round": match.get("round"),
                "source_url": match.get("source_url"),
            },
        )
        return cur.lastrowid

    def list_for_bot(self, bot_id: int) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT * FROM matches
            WHERE bot_a_id = ? OR bot_b_id = ?
            ORDER BY season DESC, episode DESC
            """,
            (bot_id, bot_id),
        ).fetchall()

    def count(self) -> int:
        return int(
            self.conn.execute("SELECT COUNT(*) AS c FROM matches").fetchone()["c"]
        )


# ---------------------------------------------------------------------------
# Sentiment
# ---------------------------------------------------------------------------
class SentimentRepository:
    """CRUD for the `sentiment` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(
        self,
        *,
        bot_id: int,
        source: str,
        positive_count: int,
        negative_count: int,
        neutral_count: int,
        sample_quotes: Iterable[Any],
    ) -> int:
        quotes_json = json.dumps(list(sample_quotes), ensure_ascii=False)
        self.conn.execute(
            """
            INSERT INTO sentiment (
                bot_id, source, positive_count, negative_count,
                neutral_count, sample_quotes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(bot_id, source) DO UPDATE SET
                positive_count = excluded.positive_count,
                negative_count = excluded.negative_count,
                neutral_count  = excluded.neutral_count,
                sample_quotes  = excluded.sample_quotes,
                scraped_at     = datetime('now')
            """,
            (
                bot_id,
                source,
                positive_count,
                negative_count,
                neutral_count,
                quotes_json,
            ),
        )
        row = self.conn.execute(
            "SELECT id FROM sentiment WHERE bot_id = ? AND source = ?",
            (bot_id, source),
        ).fetchone()
        return int(row["id"])

    def list_for_bot(self, bot_id: int) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM sentiment WHERE bot_id = ?", (bot_id,)
        ).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            try:
                raw = json.loads(data.get("sample_quotes") or "[]")
            except json.JSONDecodeError:
                raw = []
            data["sample_quotes"] = normalize_posts(raw)
            result.append(data)
        return result


# ---------------------------------------------------------------------------
# Sentiment RAG chunks
# ---------------------------------------------------------------------------
class SentimentChunkRepository:
    """Vector-ish storage for embedded Reddit posts and comments."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def replace_for_bot(
        self,
        *,
        bot_id: int,
        source: str,
        chunks: Iterable[dict[str, Any]],
    ) -> int:
        """Replace all embedded chunks for a bot/source pair."""
        self.conn.execute(
            "DELETE FROM sentiment_chunks WHERE bot_id = ? AND source = ?",
            (bot_id, source),
        )
        written = 0
        for chunk in chunks:
            self.conn.execute(
                """
                INSERT INTO sentiment_chunks (
                    bot_id, source, external_id, chunk_type, text,
                    url, metadata_json, embedding_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(bot_id, source, external_id) DO UPDATE SET
                    chunk_type = excluded.chunk_type,
                    text = excluded.text,
                    url = excluded.url,
                    metadata_json = excluded.metadata_json,
                    embedding_json = excluded.embedding_json,
                    scraped_at = datetime('now')
                """,
                (
                    bot_id,
                    source,
                    chunk["external_id"],
                    chunk["chunk_type"],
                    chunk["text"],
                    chunk.get("url"),
                    json.dumps(chunk.get("metadata") or {}, ensure_ascii=False),
                    json.dumps(chunk["embedding"], ensure_ascii=False),
                ),
            )
            written += 1
        return written

    def list_for_bot(self, bot_id: int, *, source: str = "reddit") -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM sentiment_chunks
            WHERE bot_id = ? AND source = ?
            ORDER BY id
            """,
            (bot_id, source),
        ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            data = dict(row)
            try:
                data["embedding"] = json.loads(data.pop("embedding_json") or "[]")
            except json.JSONDecodeError:
                data["embedding"] = []
            try:
                data["metadata"] = json.loads(data.pop("metadata_json") or "{}")
            except json.JSONDecodeError:
                data["metadata"] = {}
            result.append(data)
        return result

    def count_for_bot(self, bot_id: int, *, source: str = "reddit") -> int:
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS c FROM sentiment_chunks
            WHERE bot_id = ? AND source = ?
            """,
            (bot_id, source),
        ).fetchone()
        return int(row["c"]) if row else 0


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------
class PredictionRepository:
    """CRUD for the `predictions` table (used in Phase 4)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(
        self,
        *,
        bot_a_id: int,
        bot_b_id: int,
        winner_prediction: int | None,
        confidence: float | None,
        scouting_report: str,
        model: str | None,
    ) -> int:
        self.conn.execute(
            """
            INSERT INTO predictions (
                bot_a_id, bot_b_id, winner_prediction,
                confidence, scouting_report, model
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(bot_a_id, bot_b_id) DO UPDATE SET
                winner_prediction = excluded.winner_prediction,
                confidence        = excluded.confidence,
                scouting_report   = excluded.scouting_report,
                model             = excluded.model,
                created_at        = datetime('now')
            """,
            (
                bot_a_id,
                bot_b_id,
                winner_prediction,
                confidence,
                scouting_report,
                model,
            ),
        )
        row = self.conn.execute(
            "SELECT id FROM predictions WHERE bot_a_id = ? AND bot_b_id = ?",
            (bot_a_id, bot_b_id),
        ).fetchone()
        return int(row["id"])

    def get_by_id(self, prediction_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM predictions WHERE id = ?", (prediction_id,)
        ).fetchone()

    def get_for_pair(
        self, bot_a_id: int, bot_b_id: int
    ) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM predictions WHERE bot_a_id = ? AND bot_b_id = ?",
            (bot_a_id, bot_b_id),
        ).fetchone()

    def list_recent(self, limit: int = 20) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM predictions ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
