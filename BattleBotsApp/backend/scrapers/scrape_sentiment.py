"""Scrape Reddit for each bot, classify sentiment, embed for RAG, and persist.

Per bot we search configured subreddits with multiple sort orders and paginate
through results. For the highest-scoring threads we also pull comment bodies —
that's where most of the fan analysis lives.

Run via:

    python -m backend.scrapers.scrape_sentiment
    python -m backend.ai.index_sentiment   # re-embed existing rows without re-scraping
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any
from urllib.parse import quote_plus

from ..ai.rag import index_bot_sentiment
from ..config import settings
from ..db import Database, initialize_database
from ..db.repositories import BotRepository, SentimentRepository
from ..logging_setup import configure_logging
from .brightdata_client import BrightDataClient, BrightDataError
from .parsers.sentiment_parser import (
    classify_posts,
    flatten_posts_and_comments,
    parse_reddit_comments_json,
    parse_reddit_listing_json,
    parse_x_search_html,
    post_text,
)

logger = logging.getLogger(__name__)

# Sort orders: fresh chatter, high engagement, all-time hits, comment-heavy threads.
_REDDIT_SORT_ORDERS: tuple[tuple[str, str], ...] = (
    ("new", "year"),
    ("top", "year"),
    ("top", "all"),
    ("comments", "year"),
)


def _reddit_search_url(
    bot_name: str,
    *,
    sort: str = "new",
    timeframe: str = "year",
    limit: int = 100,
    subreddit: str = "Battlebots",
    after: str | None = None,
) -> str:
    query = quote_plus(f'"{bot_name}"')
    url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={query}&restrict_sr=on&sort={sort}&t={timeframe}&limit={limit}"
    )
    if after:
        url += f"&after={quote_plus(after)}"
    return url


def _reddit_comments_url(permalink: str, *, limit: int = 50) -> str:
    path = permalink if permalink.startswith("/") else f"/{permalink.lstrip('/')}"
    if not path.endswith(".json"):
        path = path.rstrip("/") + ".json"
    return f"https://www.reddit.com{path}?limit={limit}"


def _x_search_url(bot_name: str) -> str:
    query = quote_plus(f"{bot_name} battlebots")
    return f"https://x.com/search?q={query}&src=typed_query&f=live"


def _fetch_reddit_page(
    client: BrightDataClient,
    url: str,
    *,
    bot_name: str,
    context: str,
) -> tuple[list[dict[str, Any]], str | None]:
    try:
        payload = client.fetch_html(url)
    except BrightDataError as err:
        logger.warning("Reddit fetch failed (%s) for %s: %s", context, bot_name, err)
        return [], None
    return parse_reddit_listing_json(payload)


def scrape_reddit_for_bot(
    client: BrightDataClient, bot_name: str, max_quotes: int
) -> list[dict[str, Any]]:
    """Pull posts + top comments about `bot_name` from configured subreddits."""
    seen_ids: set[str] = set()
    combined: list[dict[str, Any]] = []

    for subreddit in settings.reddit_subreddit_list:
        for sort, timeframe in _REDDIT_SORT_ORDERS:
            after: str | None = None
            for page in range(settings.reddit_search_pages):
                if len(combined) >= max_quotes:
                    break
                url = _reddit_search_url(
                    bot_name,
                    sort=sort,
                    timeframe=timeframe,
                    limit=settings.reddit_search_limit,
                    subreddit=subreddit,
                    after=after,
                )
                posts, after = _fetch_reddit_page(
                    client,
                    url,
                    bot_name=bot_name,
                    context=f"r/{subreddit} sort={sort} page={page + 1}",
                )
                for post in posts:
                    post_id = post.get("id")
                    if not post_id or post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)
                    combined.append(post)
                    if len(combined) >= max_quotes:
                        break
                if not after:
                    break

    combined.sort(key=lambda p: int(p.get("score") or 0), reverse=True)

    if settings.reddit_comment_posts > 0:
        _attach_comments(client, bot_name, combined)

    flat = flatten_posts_and_comments(combined)
    if len(flat) > max_quotes:
        flat = flat[:max_quotes]

    if not flat:
        logger.info("Reddit returned 0 posts/comments for %s.", bot_name)
    else:
        logger.info(
            "Reddit gathered %d items (%d posts) for %s.",
            len(flat),
            len(combined),
            bot_name,
        )
    return flat


def _attach_comments(
    client: BrightDataClient,
    bot_name: str,
    posts: list[dict[str, Any]],
) -> None:
    """Fetch comment threads for the top-scoring posts."""
    candidates = sorted(
        posts,
        key=lambda p: int(p.get("score") or 0),
        reverse=True,
    )[: settings.reddit_comment_posts]

    for post in candidates:
        permalink = post.get("permalink")
        if not permalink:
            continue
        url = _reddit_comments_url(
            permalink, limit=settings.reddit_max_comments_per_post
        )
        try:
            payload = client.fetch_html(url)
        except BrightDataError as err:
            logger.warning(
                "Comment fetch failed for %s post %s: %s",
                bot_name,
                post.get("id"),
                err,
            )
            continue

        comments = parse_reddit_comments_json(
            payload,
            post_id=post.get("id"),
            max_comments=settings.reddit_max_comments_per_post,
        )
        if comments:
            classified = classify_posts(comments)
            post["comments"] = comments
            logger.debug(
                "    %d comments on post %s (+%d/-%d/=%d)",
                len(comments),
                post.get("id"),
                classified["positive"],
                classified["negative"],
                classified["neutral"],
            )


def scrape_x_for_bot(
    client: BrightDataClient, bot_name: str, max_quotes: int
) -> list[dict[str, Any]]:
    url = _x_search_url(bot_name)
    try:
        html = client.fetch_html(url)
    except BrightDataError as err:
        logger.warning("X fetch failed for %s: %s", bot_name, err)
        return []
    return parse_x_search_html(html, max_quotes=max_quotes)


def run(*, limit: int | None = None, sources: tuple[str, ...] = ("reddit",)) -> int:
    """Scrape sentiment for every bot in the DB. Returns total rows written."""
    settings.require_brightdata()
    initialize_database()

    written = 0
    chunks_indexed = 0
    with BrightDataClient() as client, Database() as conn:
        bots = BotRepository(conn).list_all()
        if not bots:
            logger.error(
                "No bots in the database — run scrape_bots before scrape_sentiment."
            )
            return 0

        if limit is not None:
            bots = bots[:limit]

        sentiment_repo = SentimentRepository(conn)
        max_quotes = settings.sentiment_max_quotes

        for idx, bot in enumerate(bots, start=1):
            bot_id = int(bot["id"])
            name = bot["name"]
            logger.info("[%d/%d] Gathering sentiment for %s", idx, len(bots), name)

            for source in sources:
                if source == "reddit":
                    posts = scrape_reddit_for_bot(client, name, max_quotes)
                elif source == "x":
                    posts = scrape_x_for_bot(client, name, max_quotes)
                else:
                    logger.warning("Unknown sentiment source %r; skipping.", source)
                    continue

                counts = classify_posts(posts)
                sentiment_repo.upsert(
                    bot_id=bot_id,
                    source=source,
                    positive_count=counts["positive"],
                    negative_count=counts["negative"],
                    neutral_count=counts["neutral"],
                    sample_quotes=posts,
                )
                written += 1
                chunks_indexed += index_bot_sentiment(
                    conn, bot_id=bot_id, source=source, posts=posts
                )
                logger.info(
                    "    %s: %d items (+%d / -%d / =%d)",
                    source,
                    len(posts),
                    counts["positive"],
                    counts["negative"],
                    counts["neutral"],
                )

    logger.info(
        "Done. %d sentiment rows upserted, %d RAG chunks indexed.",
        written,
        chunks_indexed,
    )
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape Reddit (+ optional X) sentiment per bot and index for RAG."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N bots (useful for quick test runs).",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["reddit"],
        choices=["reddit", "x"],
        help="Which sources to scrape. Reddit is the default.",
    )
    args = parser.parse_args()
    configure_logging()
    try:
        run(limit=args.limit, sources=tuple(args.sources))
    except RuntimeError as err:
        logger.error(str(err))
        sys.exit(1)


if __name__ == "__main__":
    main()
