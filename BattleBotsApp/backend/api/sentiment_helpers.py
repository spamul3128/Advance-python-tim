"""Shared helpers for serializing sentiment rows to API models."""

from __future__ import annotations

from typing import Any

from ..scrapers.parsers.sentiment_parser import normalize_posts, posts_to_quotes
from .schemas import ExplorerSentimentRow, SentimentItem, SentimentPost


def sentiment_item_from_row(row: dict[str, Any]) -> SentimentItem:
    """Build a SentimentItem from a DB row, normalizing legacy string quotes."""
    posts_raw = normalize_posts(row.get("sample_quotes"))
    posts = [_post_model(p) for p in posts_raw]
    return SentimentItem(
        source=row["source"],
        positive_count=row["positive_count"],
        negative_count=row["negative_count"],
        neutral_count=row["neutral_count"],
        posts=posts,
        sample_quotes=posts_to_quotes(posts_raw),
    )


def _post_model(post: dict[str, Any]) -> SentimentPost:
    return SentimentPost(
        id=post.get("id"),
        title=post.get("title") or "",
        body=post.get("body"),
        url=post.get("url"),
        score=post.get("score"),
        num_comments=post.get("num_comments"),
        created_at=post.get("created_at"),
        subreddit=post.get("subreddit"),
        sentiment=post.get("sentiment"),
        text=post.get("text") or "",
    )


def explorer_sentiment_row_from_dict(data: dict[str, Any]) -> ExplorerSentimentRow:
    """Build an explorer row with normalized post objects."""
    posts_raw = normalize_posts(data.get("sample_quotes"))
    posts = [_post_model(p) for p in posts_raw]
    return ExplorerSentimentRow(
        id=data["id"],
        bot_id=data.get("bot_id"),
        bot_name=data.get("bot_name"),
        source=data["source"],
        positive_count=data["positive_count"],
        negative_count=data["negative_count"],
        neutral_count=data["neutral_count"],
        posts=posts,
        sample_quotes=posts_to_quotes(posts_raw),
        scraped_at=data.get("scraped_at"),
    )
