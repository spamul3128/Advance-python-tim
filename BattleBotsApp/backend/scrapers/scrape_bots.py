"""Scrape BattleBots bot profiles and persist them to SQLite.

Pipeline:

1. Try to scrape https://battlebots.com/the-bots/ for a list of (name, url).
2. If that yields fewer than `MIN_BOTS_FROM_LISTING`, fall back to the
   curated `SEED_BOT_ROSTER`.
3. For each bot:
     a. Fetch the official profile page (if we have a URL).
     b. Fetch the Fandom wiki page.
     c. Merge the two — official data wins, wiki fills gaps.
     d. Upsert into the `bots` table.

Run via:

    python -m backend.scrapers.scrape_bots
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from ..config import settings
from ..db import Database, initialize_database
from ..db.repositories import BotRepository
from ..logging_setup import configure_logging
from .brightdata_client import BrightDataClient, BrightDataError
from .parsers.bots_parser import (
    parse_bot_listing_from_official_site,
    parse_bot_profile_from_fandom,
    parse_bot_profile_from_official_site,
)
from .seed_data import (
    BATTLEBOTS_LISTING_URL,
    MIN_BOTS_FROM_LISTING,
    SEED_BOT_ROSTER,
    fandom_url_for,
)

logger = logging.getLogger(__name__)


def collect_bot_targets(client: BrightDataClient) -> list[dict[str, str]]:
    """Return a list of `{name, official_url?, fandom_url}` dicts to scrape."""
    listing_targets: list[dict[str, str]] = []

    try:
        logger.info("Fetching official bot listing from %s", BATTLEBOTS_LISTING_URL)
        html = client.fetch_html(BATTLEBOTS_LISTING_URL)
        listing_targets = parse_bot_listing_from_official_site(html)
        logger.info("Found %d bots from official listing.", len(listing_targets))
    except BrightDataError as err:
        logger.warning("Could not scrape official listing: %s", err)

    targets: list[dict[str, str]] = []
    seen_names: set[str] = set()

    if len(listing_targets) >= MIN_BOTS_FROM_LISTING:
        for item in listing_targets:
            name = item["name"]
            if name.lower() in seen_names:
                continue
            seen_names.add(name.lower())
            targets.append(
                {
                    "name": name,
                    "official_url": item["url"],
                    "fandom_url": fandom_url_for(_to_fandom_slug(name)),
                }
            )
    else:
        logger.info(
            "Official listing returned %d bots (< %d). Using seed roster.",
            len(listing_targets),
            MIN_BOTS_FROM_LISTING,
        )

    # Merge in seed roster for any bots not already covered.
    for seed in SEED_BOT_ROSTER:
        name = seed["name"]
        if name.lower() in seen_names:
            continue
        seen_names.add(name.lower())
        targets.append(
            {
                "name": name,
                "official_url": "",
                "fandom_url": fandom_url_for(seed["fandom_slug"]),
            }
        )

    return targets


def scrape_single_bot(
    client: BrightDataClient, target: dict[str, str]
) -> dict[str, Any] | None:
    """Fetch + parse both sources for one bot, return merged record."""
    official_data: dict[str, Any] = {}
    fandom_data: dict[str, Any] = {}

    if target.get("official_url"):
        try:
            html = client.fetch_html(target["official_url"])
            official_data = parse_bot_profile_from_official_site(
                html, source_url=target["official_url"]
            )
        except BrightDataError as err:
            logger.warning(
                "Official profile fetch failed for %s: %s", target["name"], err
            )

    if target.get("fandom_url"):
        try:
            html = client.fetch_html(target["fandom_url"])
            fandom_data = parse_bot_profile_from_fandom(
                html, source_url=target["fandom_url"]
            )
        except BrightDataError as err:
            logger.warning(
                "Fandom profile fetch failed for %s: %s", target["name"], err
            )

    merged = _merge_bot_records(target["name"], official_data, fandom_data)
    if not merged.get("name"):
        return None
    return merged


def _merge_bot_records(
    fallback_name: str,
    official: dict[str, Any],
    fandom: dict[str, Any],
) -> dict[str, Any]:
    """Prefer official data, but use Fandom to fill missing fields."""
    merged: dict[str, Any] = {}
    fields = (
        "name", "weight_class", "weapon_type", "weapon_description",
        "team_name", "country", "image_url", "description", "source_url",
    )
    for field in fields:
        merged[field] = (
            (official.get(field) or "").strip() if isinstance(official.get(field), str)
            else official.get(field)
        ) or fandom.get(field)

    if not merged.get("name"):
        merged["name"] = fallback_name

    # Prefer the source_url that actually produced data.
    if not merged.get("source_url"):
        merged["source_url"] = official.get("source_url") or fandom.get("source_url")
    return merged


def _to_fandom_slug(name: str) -> str:
    """Convert a display name to a Fandom URL slug.

    Fandom slugs URL-encode spaces as underscores and preserve case + most
    punctuation. Real-world examples:
        "Witch Doctor" -> "Witch_Doctor"
        "Lock-Jaw"     -> "Lock-Jaw"
        "Black Dragon" -> "Black_Dragon"
    """
    return name.strip().replace(" ", "_")


def run(*, limit: int | None = None) -> int:
    """Scrape all bots and persist them. Returns the number written."""
    settings.require_brightdata()
    initialize_database()

    written = 0
    with BrightDataClient() as client:
        targets = collect_bot_targets(client)
        logger.info("Scraping %d bot profiles...", len(targets))

        if limit is not None:
            targets = targets[:limit]

        with Database() as conn:
            repo = BotRepository(conn)
            for idx, target in enumerate(targets, start=1):
                try:
                    record = scrape_single_bot(client, target)
                except Exception as err:  # noqa: BLE001 — log + continue.
                    logger.exception("Unexpected error scraping %s: %s", target["name"], err)
                    continue

                if not record:
                    logger.warning("No data extracted for %s; skipping.", target["name"])
                    continue

                bot_id = repo.upsert(record)
                written += 1
                logger.info(
                    "[%d/%d] Saved bot id=%d name=%s (weapon=%s, team=%s)",
                    idx,
                    len(targets),
                    bot_id,
                    record["name"],
                    record.get("weapon_type") or "?",
                    record.get("team_name") or "?",
                )

    logger.info("Done. %d bots upserted.", written)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape BattleBots bot profiles.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only scrape the first N bots (useful for quick test runs).",
    )
    args = parser.parse_args()
    configure_logging()
    try:
        run(limit=args.limit)
    except RuntimeError as err:
        logger.error(str(err))
        sys.exit(1)


if __name__ == "__main__":
    main()
