"""Parsers + keyword-based sentiment classification.

Two transport formats:

- Reddit:  we hit `https://www.reddit.com/search.json` via Bright Data and
  parse the JSON response. JSON is far more reliable than scraping the HTML.

- X (Twitter): we fetch `https://x.com/search?q=<bot>+battlebots&src=typed_query`
  via Bright Data and extract textual content from tweet articles. X is
  heavily anti-bot — Bright Data Web Unlocker helps but coverage is best-effort.

Each scraped item is stored as a structured post dict (title, body, url, …)
so the UI can link back to the original thread. The composed `text` field
is kept for LLM prompts.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


_POSITIVE_WORDS = {
    "amazing", "awesome", "best", "champion", "champ", "crushed", "decimated",
    "destroyed", "dominant", "dominated", "excellent", "favorite", "fantastic",
    "fearsome", "goat", "great", "incredible", "insane", "killer", "legend",
    "legendary", "love", "loved", "obliterated", "powerful", "smashed",
    "spectacular", "stellar", "strong", "stunning", "terrifying", "underrated",
    "unstoppable", "won", "winner", "wonderful",
}

_NEGATIVE_WORDS = {
    "bad", "boring", "broke", "broken", "busted", "destroyed by", "disappointing",
    "garbage", "gimmick", "hate", "horrible", "lame", "lost", "loser", "meh",
    "overrated", "pathetic", "poor", "ruined", "terrible", "trash", "ugly",
    "underwhelming", "weak",
}


def classify_text(text: str) -> str:
    """Classify a single text blob as positive / negative / neutral."""
    lowered = text.lower()
    pos_hits = sum(1 for w in _POSITIVE_WORDS if w in lowered)
    neg_hits = sum(1 for w in _NEGATIVE_WORDS if w in lowered)
    if pos_hits > neg_hits:
        return "positive"
    if neg_hits > pos_hits:
        return "negative"
    return "neutral"


def classify_quotes(quotes: list[str]) -> dict[str, int]:
    """Bucket quote strings into positive / negative / neutral counts."""
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for raw in quotes:
        counts[classify_text(raw)] += 1
    return counts


def classify_posts(posts: list[dict[str, Any]]) -> dict[str, int]:
    """Classify structured posts in-place and return aggregate counts."""
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for post in posts:
        label = classify_text(post_text(post))
        post["sentiment"] = label
        counts[label] += 1
    return counts


def post_text(post: dict[str, Any]) -> str:
    """Best string representation of a post for classification / LLM."""
    if post.get("text"):
        return str(post["text"])
    title = (post.get("title") or "").strip()
    body = (post.get("body") or "").strip()
    return " — ".join(part for part in (title, body) if part)


def posts_to_quotes(posts: list[dict[str, Any]]) -> list[str]:
    """Legacy string list derived from structured posts."""
    return [post_text(p) for p in posts if post_text(p)]


def normalize_posts(raw: list[Any] | None) -> list[dict[str, Any]]:
    """Convert stored JSON (legacy strings or objects) to post dicts."""
    if not raw:
        return []
    result: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, str):
            label = classify_text(item)
            # Legacy strings embed metadata in brackets — treat whole string as title.
            result.append(
                {
                    "title": item,
                    "body": None,
                    "url": None,
                    "text": item,
                    "sentiment": label,
                }
            )
        elif isinstance(item, dict):
            post = dict(item)
            if not post.get("sentiment"):
                post["sentiment"] = classify_text(post_text(post))
            if not post.get("text"):
                post["text"] = post_text(post)
            result.append(post)
    return result


# ---------------------------------------------------------------------------
# Reddit
# ---------------------------------------------------------------------------
def parse_reddit_search_json(
    payload: str,
    max_quotes: int,
    *,
    include_metadata: bool = True,
) -> list[dict[str, Any]]:
    """Extract structured posts from a Reddit search JSON response.

    Returns dicts with keys: id, title, body, url, score, num_comments,
    created_at, subreddit, text (composed for LLM).
    """
    try:
        doc = json.loads(payload)
    except json.JSONDecodeError as err:
        logger.warning("Reddit response was not valid JSON: %s", err)
        return []

    children = (doc.get("data") or {}).get("children") or []
    posts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for child in children:
        data = child.get("data") or {}
        post_id = data.get("id") or ""
        if post_id:
            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

        title = (data.get("title") or "").strip()
        body = (data.get("selftext") or "").strip()
        if not title and not body:
            continue

        created_at = _reddit_created_at(data)
        prefix = _format_reddit_prefix(data) if include_metadata else ""
        composed = _compose_post_text(title, body, prefix=prefix)

        posts.append(
            {
                "id": post_id or None,
                "title": title or "(untitled)",
                "body": body or None,
                "url": _reddit_post_url(data),
                "score": int(data.get("score") or 0),
                "num_comments": int(data.get("num_comments") or 0),
                "created_at": created_at,
                "subreddit": data.get("subreddit") or None,
                "text": _truncate(composed, 480),
            }
        )

    posts.sort(key=lambda p: _created_sort_key(p.get("created_at")), reverse=True)
    return posts[:max_quotes]


def parse_reddit_listing_json(
    payload: str,
    *,
    include_metadata: bool = True,
) -> tuple[list[dict[str, Any]], str | None]:
    """Parse one Reddit listing page and return posts plus pagination cursor."""
    try:
        doc = json.loads(payload)
    except json.JSONDecodeError as err:
        logger.warning("Reddit response was not valid JSON: %s", err)
        return [], None

    children = (doc.get("data") or {}).get("children") or []
    after = (doc.get("data") or {}).get("after")
    posts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for child in children:
        data = child.get("data") or {}
        post_id = data.get("id") or ""
        if post_id:
            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

        title = (data.get("title") or "").strip()
        body = (data.get("selftext") or "").strip()
        if not title and not body:
            continue

        created_at = _reddit_created_at(data)
        prefix = _format_reddit_prefix(data) if include_metadata else ""
        composed = _compose_post_text(title, body, prefix=prefix)
        permalink = (data.get("permalink") or "").strip()

        posts.append(
            {
                "id": post_id or None,
                "type": "post",
                "title": title or "(untitled)",
                "body": body or None,
                "url": _reddit_post_url(data),
                "permalink": permalink or None,
                "score": int(data.get("score") or 0),
                "num_comments": int(data.get("num_comments") or 0),
                "created_at": created_at,
                "subreddit": data.get("subreddit") or None,
                "text": _truncate(composed, 800),
            }
        )

    posts.sort(key=lambda p: _created_sort_key(p.get("created_at")), reverse=True)
    return posts, after if after else None


def parse_reddit_comments_json(
    payload: str,
    *,
    post_id: str | None = None,
    max_comments: int = 30,
) -> list[dict[str, Any]]:
    """Extract top-level comments from a Reddit thread `.json` response."""
    try:
        doc = json.loads(payload)
    except json.JSONDecodeError as err:
        logger.warning("Reddit comments response was not valid JSON: %s", err)
        return []

    if not isinstance(doc, list) or len(doc) < 2:
        return []

    comment_listing = doc[1].get("data") or {}
    children = comment_listing.get("children") or []
    comments: list[dict[str, Any]] = []

    for child in children:
        if child.get("kind") != "t1":
            continue
        data = child.get("data") or {}
        body = (data.get("body") or "").strip()
        if not body or body in {"[deleted]", "[removed]"}:
            continue

        comment_id = data.get("id") or ""
        created_at = _reddit_created_at(data)
        prefix = _format_reddit_prefix(data)
        composed = _truncate(f"{prefix}{body}", 800)
        permalink = (data.get("permalink") or "").strip()

        comments.append(
            {
                "id": comment_id or None,
                "type": "comment",
                "parent_id": post_id,
                "title": None,
                "body": body,
                "url": (
                    f"https://www.reddit.com{permalink}"
                    if permalink and not permalink.startswith("http")
                    else permalink or None
                ),
                "score": int(data.get("score") or 0),
                "num_comments": None,
                "created_at": created_at,
                "subreddit": data.get("subreddit") or None,
                "text": composed,
            }
        )
        if len(comments) >= max_comments:
            break

    comments.sort(key=lambda c: int(c.get("score") or 0), reverse=True)
    return comments


def flatten_posts_and_comments(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expand nested `comments` arrays into a flat list for storage."""
    flat: list[dict[str, Any]] = []
    for post in posts:
        entry = {k: v for k, v in post.items() if k != "comments"}
        flat.append(entry)
        for comment in post.get("comments") or []:
            flat.append(comment)
    return flat


def _compose_post_text(title: str, body: str, *, prefix: str = "") -> str:
    body_text = " — ".join(part for part in (title, body) if part)
    return f"{prefix}{body_text}" if prefix else body_text


def _reddit_created_at(data: dict[str, Any]) -> str | None:
    if not data.get("created_utc"):
        return None
    try:
        return datetime.fromtimestamp(
            float(data["created_utc"]), tz=timezone.utc
        ).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _created_sort_key(created_at: str | None) -> float:
    if not created_at:
        return 0.0
    try:
        return datetime.strptime(created_at, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        ).timestamp()
    except ValueError:
        return 0.0


def _reddit_post_url(data: dict[str, Any]) -> str | None:
    """Prefer the Reddit permalink; fall back to the post URL."""
    permalink = (data.get("permalink") or "").strip()
    if permalink:
        if permalink.startswith("http"):
            return permalink
        return f"https://www.reddit.com{permalink}"

    url = (data.get("url") or "").strip()
    return url or None


def _format_reddit_prefix(data: dict[str, Any]) -> str:
    """Build a `[date · score↑ · N comments · r/sub]` prefix for a post."""
    parts: list[str] = []
    when = _reddit_created_at(data)
    if when:
        parts.append(when)
    if data.get("score") is not None:
        parts.append(f"{data['score']}\u2191")
    if data.get("num_comments") is not None:
        parts.append(f"{data['num_comments']} comments")
    subreddit = data.get("subreddit") or ""
    if subreddit:
        parts.append(f"r/{subreddit}")
    if not parts:
        return ""
    return f"[{' \u00b7 '.join(parts)}] "


# ---------------------------------------------------------------------------
# X (Twitter)
# ---------------------------------------------------------------------------
def parse_x_search_html(html: str, max_quotes: int) -> list[dict[str, Any]]:
    """Extract tweet text from an X search results page."""
    soup = BeautifulSoup(html, "lxml")
    posts: list[dict[str, Any]] = []

    for article in soup.find_all("article"):
        text_node = article.select_one("[data-testid='tweetText']")
        text = (
            text_node.get_text(" ", strip=True)
            if text_node
            else article.get_text(" ", strip=True)
        )
        text = re.sub(r"\s+", " ", text).strip()
        if text and len(text) > 20:
            posts.append(_x_post_from_text(text))
        if len(posts) >= max_quotes:
            break

    if posts:
        return posts

    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if text and len(text) > 40:
            posts.append(_x_post_from_text(text))
        if len(posts) >= max_quotes:
            break

    return posts


def _x_post_from_text(text: str) -> dict[str, Any]:
    truncated = _truncate(text, 400)
    return {
        "id": None,
        "title": truncated,
        "body": None,
        "url": None,
        "score": None,
        "num_comments": None,
        "created_at": None,
        "subreddit": None,
        "text": truncated,
    }


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
