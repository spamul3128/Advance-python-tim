"""Basic RAG pipeline for Reddit sentiment — chunk, embed, retrieve."""

from __future__ import annotations

import logging
import sqlite3
from typing import Any

from ..config import settings
from ..db.repositories import SentimentChunkRepository
from ..scrapers.parsers.sentiment_parser import post_text
from .embeddings import embed_texts

logger = logging.getLogger(__name__)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def posts_to_chunk_records(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Turn scraped posts/comments into indexable chunk records (no embeddings yet)."""
    records: list[dict[str, Any]] = []
    for item in posts:
        text = post_text(item).strip()
        if len(text) < 20:
            continue
        external_id = item.get("id")
        if not external_id:
            continue
        chunk_type = item.get("type") or "post"
        parent = item.get("parent_id")
        if chunk_type == "comment" and parent:
            external_id = f"{parent}:{external_id}"

        records.append(
            {
                "external_id": str(external_id),
                "chunk_type": chunk_type,
                "text": text,
                "url": item.get("url"),
                "metadata": {
                    "score": item.get("score"),
                    "subreddit": item.get("subreddit"),
                    "sentiment": item.get("sentiment"),
                    "created_at": item.get("created_at"),
                },
            }
        )
    return records


def index_bot_sentiment(
    conn: sqlite3.Connection,
    *,
    bot_id: int,
    source: str,
    posts: list[dict[str, Any]],
) -> int:
    """Embed and persist sentiment chunks for one bot. Returns chunk count."""
    if not settings.can_embed():
        logger.debug("RAG indexing skipped — embeddings not configured.")
        return 0

    records = posts_to_chunk_records(posts)
    if not records:
        return 0

    try:
        vectors = embed_texts([r["text"] for r in records])
    except Exception as err:
        logger.warning("Embedding failed for bot_id=%d: %s", bot_id, err)
        return 0

    for record, vector in zip(records, vectors):
        record["embedding"] = vector

    repo = SentimentChunkRepository(conn)
    count = repo.replace_for_bot(bot_id=bot_id, source=source, chunks=records)
    logger.info(
        "Indexed %d sentiment chunks for bot_id=%d (%s)",
        count,
        bot_id,
        source,
    )
    return count


def retrieve_sentiment_chunks(
    conn: sqlite3.Connection,
    *,
    bot_id: int,
    query: str,
    top_k: int | None = None,
    source: str = "reddit",
) -> list[dict[str, Any]]:
    """Return the top-K Reddit chunks most similar to `query` for a bot."""
    if not settings.can_embed():
        return []

    k = top_k or settings.rag_top_k_per_bot
    stored = SentimentChunkRepository(conn).list_for_bot(bot_id, source=source)
    if not stored:
        return []

    try:
        query_vector = embed_texts([query])[0]
    except Exception as err:
        logger.warning("Query embedding failed: %s", err)
        return []

    scored: list[tuple[float, dict[str, Any]]] = []
    for row in stored:
        vector = row.get("embedding") or []
        score = cosine_similarity(query_vector, vector)
        if score <= 0:
            continue
        item = dict(row)
        item["similarity"] = round(score, 4)
        scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:k]]


def build_matchup_query(bot_a_name: str, bot_b_name: str) -> str:
    """Search query used when retrieving fan sentiment for a prediction."""
    return (
        f"{bot_a_name} vs {bot_b_name} BattleBots matchup "
        f"weapon strategy strengths weaknesses fan opinion"
    )
