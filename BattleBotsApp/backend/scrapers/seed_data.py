"""Seed lists used by the scrapers.

These hard-coded URLs give the pipeline a deterministic starting point. The
official BattleBots listing page is JS-heavy and its DOM changes often, so
seed data acts as a reliable fallback.

When a user re-runs scrapers later in the season they can edit this file to
add the latest roster — no code changes needed elsewhere.
"""

from __future__ import annotations

# Pages to scrape for tournament results. Add more seasons as needed.
# Each page is parsed by `matches_parser.parse_match_tables`.
TOURNAMENT_PAGES: tuple[dict[str, str], ...] = (
    {
        "season": "World Championship VIII",
        "url": "https://battlebots.fandom.com/wiki/World_Championship_VIII",
    },
    {
        "season": "World Championship VII",
        "url": "https://battlebots.fandom.com/wiki/World_Championship_VII",
    },
    {
        "season": "World Championship VI",
        "url": "https://battlebots.fandom.com/wiki/World_Championship_VI",
    },
    {
        "season": "World Championship V",
        "url": "https://battlebots.fandom.com/wiki/World_Championship_V",
    },
)


# Fallback bot roster. Used when the listing page scrape returns nothing or
# fewer than `MIN_BOTS_FROM_LISTING` entries. Each entry pairs a display name
# with a Fandom wiki slug — battlebots.fandom.com/wiki/<slug>.
SEED_BOT_ROSTER: tuple[dict[str, str], ...] = (
    {"name": "Tombstone", "fandom_slug": "Tombstone"},
    {"name": "HUGE", "fandom_slug": "HUGE"},
    {"name": "Witch Doctor", "fandom_slug": "Witch_Doctor"},
    {"name": "End Game", "fandom_slug": "End_Game"},
    {"name": "Bloodsport", "fandom_slug": "Bloodsport"},
    {"name": "Hydra", "fandom_slug": "Hydra"},
    {"name": "Minotaur", "fandom_slug": "Minotaur"},
    {"name": "Whiplash", "fandom_slug": "Whiplash"},
    {"name": "SawBlaze", "fandom_slug": "SawBlaze"},
    {"name": "Hypershock", "fandom_slug": "Hypershock"},
    {"name": "Yeti", "fandom_slug": "Yeti"},
    {"name": "Lock-Jaw", "fandom_slug": "Lock-Jaw"},
    {"name": "Black Dragon", "fandom_slug": "Black_Dragon"},
    {"name": "Bite Force", "fandom_slug": "Bite_Force"},
    {"name": "Rotator", "fandom_slug": "Rotator"},
    {"name": "Riptide", "fandom_slug": "Riptide"},
    {"name": "Copperhead", "fandom_slug": "Copperhead"},
    {"name": "Mammoth", "fandom_slug": "Mammoth"},
    {"name": "Skorpios", "fandom_slug": "Skorpios"},
    {"name": "Valkyrie", "fandom_slug": "Valkyrie"},
    {"name": "Uppercut", "fandom_slug": "Uppercut"},
    {"name": "Gigabyte", "fandom_slug": "Gigabyte"},
    {"name": "Cobalt", "fandom_slug": "Cobalt"},
    {"name": "Ribbot", "fandom_slug": "Ribbot"},
)


BATTLEBOTS_LISTING_URL = "https://battlebots.com/the-bots/"

# Minimum number of bots we expect to scrape from the official listing.
# If fewer are returned, we fall back to SEED_BOT_ROSTER.
MIN_BOTS_FROM_LISTING = 10


def fandom_url_for(slug: str) -> str:
    return f"https://battlebots.fandom.com/wiki/{slug}"
