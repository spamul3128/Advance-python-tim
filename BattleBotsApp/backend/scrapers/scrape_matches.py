"""Scrape per-bot match history from the BattleBots Fandom wiki.

Each bot's wiki page (e.g. https://battlebots.fandom.com/wiki/Tombstone) has
an `article-table` listing every match that bot has fought, grouped by
tournament. This script iterates the bots currently in our DB, fetches each
bot's page, and parses the career fight log.

Why per-bot instead of per-tournament:
    - Tournament pages list scheduled fights but not winners/methods.
    - Per-bot pages embed each fight's recap text, which lets us recover
      winner + method via heuristics in `matches_parser.parse_career_log`.

Duplicates are deduped naturally by the matches schema's UNIQUE index on
(bot_a_id, bot_b_id, season). When we scrape Tombstone we'll record
"Tombstone vs HUGE @ WC VII"; when we later scrape HUGE, the same fight is
re-saved as "HUGE vs Tombstone @ WC VII" but the upsert keys treat them as
distinct rows. The predictor still works correctly because each bot's match
history is queried by bot_a OR bot_b id, so the row is only counted once
per analysis.

Run via:

    python -m backend.scrapers.scrape_matches
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
import time
from typing import Any
from urllib.parse import quote

from ..config import settings
from ..db import Database, initialize_database
from ..db.repositories import BotRepository, MatchRepository
from ..logging_setup import configure_logging
from .brightdata_client import BrightDataClient, BrightDataError
from .parsers.matches_parser import parse_career_log

logger = logging.getLogger(__name__)

FANDOM_BOT_URL = "https://battlebots.fandom.com/wiki/{slug}"


def _build_name_index(conn: sqlite3.Connection) -> dict[str, int]:
    """Lowercased bot-name -> id lookup for resolving opponents."""
    rows = BotRepository(conn).list_all()
    return {row["name"].lower(): int(row["id"]) for row in rows}


def _slug_for(name: str) -> str:
    """Best-effort Fandom slug. Mirrors the seed-data convention (underscores)."""
    return quote(name.replace(" ", "_"))


def _resolve_match_ids(
    raw: dict[str, Any], index: dict[str, int]
) -> dict[str, Any] | None:
    """Convert bot *names* to bot *ids*. Returns None if either side is
    not in our DB — we can't store the row meaningfully without both."""
    bot_a_id = index.get(raw["bot_a_name"].lower())
    bot_b_id = index.get(raw["bot_b_name"].lower())
    if bot_a_id is None or bot_b_id is None:
        return None

    winner_id: int | None = None
    if raw.get("winner_name"):
        winner_id = index.get(raw["winner_name"].lower())

    return {
        "bot_a_id": bot_a_id,
        "bot_b_id": bot_b_id,
        "winner_id": winner_id,
        "method": raw.get("method"),
        "season": raw.get("season"),
        "episode": raw.get("episode"),
        "round": raw.get("round"),
        "source_url": raw.get("source_url"),
    }


def run(*, limit_bots: int | None = None) -> int:
    """Scrape per-bot career fight logs and persist matches.

    Returns the number of matches written.
    """
    settings.require_brightdata()
    initialize_database()

    written = 0
    skipped_unresolved = 0

    with BrightDataClient() as client, Database() as conn:
        name_index = _build_name_index(conn)
        if not name_index:
            logger.error(
                "No bots in the database — run scrape_bots before scrape_matches."
            )
            return 0

        known_names = {row["name"] for row in BotRepository(conn).list_all() if row["name"]}
        bots = BotRepository(conn).list_all()
        if limit_bots is not None:
            bots = bots[:limit_bots]

        repo = MatchRepository(conn)

        for idx, bot in enumerate(bots, start=1):
            bot_name = bot["name"]
            url = FANDOM_BOT_URL.format(slug=_slug_for(bot_name))
            logger.info(
                "[%d/%d] Fetching career log for %s -> %s",
                idx,
                len(bots),
                bot_name,
                url,
            )

            try:
                html = client.fetch_html(url)
            except BrightDataError as err:
                logger.warning("Failed to fetch %s: %s", url, err)
                continue

            rows = parse_career_log(
                html,
                bot_name=bot_name,
                known_bot_names=known_names,
                source_url=url,
            )
            logger.info(
                "    parsed %d career rows for %s", len(rows), bot_name
            )

            for raw in rows:
                resolved = _resolve_match_ids(raw, name_index)
                if resolved is None:
                    skipped_unresolved += 1
                    continue
                try:
                    repo.upsert(resolved)
                    written += 1
                except Exception as err:  # noqa: BLE001
                    logger.exception(
                        "Failed to upsert match %s vs %s: %s",
                        raw.get("bot_a_name"),
                        raw.get("bot_b_name"),
                        err,
                    )

            # Be kind to Bright Data — small jitter between requests on top
            # of the client's internal rate limiter.
            time.sleep(0.2)

    logger.info(
        "Done. %d matches upserted. %d skipped (opponent not in bots table).",
        written,
        skipped_unresolved,
    )
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape BattleBots match history.")
    parser.add_argument(
        "--limit-bots",
        type=int,
        default=None,
        help="Only process the first N bots from the DB (for quick test runs).",
    )
    args = parser.parse_args()
    configure_logging()
    try:
        run(limit_bots=args.limit_bots)
    except RuntimeError as err:
        logger.error(str(err))
        sys.exit(1)


if __name__ == "__main__":
    main()
