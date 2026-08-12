"""Run all three scrapers in dependency order.

Order matters:
    1. scrape_bots      — populates the `bots` table.
    2. scrape_matches   — needs bot ids to resolve competitors.
    3. scrape_sentiment — iterates the rows in `bots` to know who to search.

Run via:

    python -m backend.scrapers.run_all_scrapers

Flags::

    --skip-bots         Skip the bot-profile scrape.
    --skip-matches      Skip the match-history scrape.
    --skip-sentiment    Skip the sentiment scrape.
    --limit-bots N      Only scrape the first N bots (for quick smoke tests).
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from ..config import settings
from ..logging_setup import configure_logging
from . import scrape_bots, scrape_matches, scrape_sentiment

logger = logging.getLogger(__name__)


def run(
    *,
    skip_bots: bool = False,
    skip_matches: bool = False,
    skip_sentiment: bool = False,
    limit_bots: int | None = None,
    sentiment_sources: tuple[str, ...] = ("reddit",),
) -> dict[str, int]:
    """Execute all enabled stages. Returns a per-stage count summary.

    `sentiment_sources` defaults to Reddit only because X.com aggressively
    rate-limits unauthenticated scraping, including via Bright Data. Pass
    `("reddit", "x")` to opt back in (expect long timeouts).
    """
    settings.require_brightdata()
    started = time.monotonic()
    summary: dict[str, int] = {"bots": 0, "matches": 0, "sentiment": 0}

    if not skip_bots:
        logger.info("=== Stage 1/3: scraping bot profiles ===")
        summary["bots"] = scrape_bots.run(limit=limit_bots)
    else:
        logger.info("=== Stage 1/3: SKIPPED (bots) ===")

    if not skip_matches:
        logger.info("=== Stage 2/3: scraping match history ===")
        summary["matches"] = scrape_matches.run(limit_bots=limit_bots)
    else:
        logger.info("=== Stage 2/3: SKIPPED (matches) ===")

    if not skip_sentiment:
        logger.info(
            "=== Stage 3/3: scraping sentiment (%s) ===",
            ", ".join(sentiment_sources),
        )
        summary["sentiment"] = scrape_sentiment.run(
            limit=limit_bots, sources=sentiment_sources
        )
    else:
        logger.info("=== Stage 3/3: SKIPPED (sentiment) ===")

    duration = time.monotonic() - started
    logger.info(
        "All done in %.1fs. bots=%d matches=%d sentiment=%d",
        duration,
        summary["bots"],
        summary["matches"],
        summary["sentiment"],
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all BattleBots scrapers.")
    parser.add_argument("--skip-bots", action="store_true")
    parser.add_argument("--skip-matches", action="store_true")
    parser.add_argument("--skip-sentiment", action="store_true")
    parser.add_argument(
        "--limit-bots",
        type=int,
        default=None,
        help="Cap the number of bots processed by bot + sentiment stages.",
    )
    parser.add_argument(
        "--sentiment-sources",
        nargs="+",
        default=["reddit"],
        choices=["reddit", "x"],
        help="Which sentiment sources to scrape (default: reddit only).",
    )
    args = parser.parse_args()
    configure_logging()
    try:
        run(
            skip_bots=args.skip_bots,
            skip_matches=args.skip_matches,
            skip_sentiment=args.skip_sentiment,
            limit_bots=args.limit_bots,
            sentiment_sources=tuple(args.sentiment_sources),
        )
    except RuntimeError as err:
        logger.error(str(err))
        sys.exit(1)


if __name__ == "__main__":
    main()
