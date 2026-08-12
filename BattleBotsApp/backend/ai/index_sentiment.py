"""Re-embed existing sentiment rows into the RAG chunk store without re-scraping.

Run via:

    python -m backend.ai.index_sentiment
    python -m backend.ai.index_sentiment --limit 5
"""

from __future__ import annotations

import argparse
import logging
import sys

from ..config import settings
from ..db import Database, initialize_database
from ..db.repositories import BotRepository, SentimentRepository
from ..logging_setup import configure_logging
from ..scrapers.parsers.sentiment_parser import normalize_posts
from .rag import index_bot_sentiment

logger = logging.getLogger(__name__)


def run(*, limit: int | None = None) -> int:
    if not settings.can_embed():
        raise RuntimeError(
            "RAG indexing requires OPENAI_API_KEY and RAG_ENABLED=true in backend/.env."
        )

    initialize_database()
    indexed = 0

    with Database() as conn:
        bots = BotRepository(conn).list_all()
        if limit is not None:
            bots = bots[:limit]

        sentiment_repo = SentimentRepository(conn)
        for bot in bots:
            bot_id = int(bot["id"])
            rows = sentiment_repo.list_for_bot(bot_id)
            for row in rows:
                source = row.get("source") or "reddit"
                posts = normalize_posts(row.get("sample_quotes"))
                if not posts:
                    continue
                count = index_bot_sentiment(
                    conn, bot_id=bot_id, source=source, posts=posts
                )
                indexed += count
                logger.info(
                    "Re-indexed %d chunks for %s (%s)",
                    count,
                    bot["name"],
                    source,
                )

    logger.info("Done. %d total chunks indexed.", indexed)
    return indexed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Embed existing sentiment quotes into the RAG chunk store."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N bots.",
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
