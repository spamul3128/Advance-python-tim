"""Tests for sentiment classification and source-specific parsers."""

from __future__ import annotations

import json

from backend.scrapers.parsers.sentiment_parser import (
    classify_posts,
    classify_quotes,
    normalize_posts,
    parse_reddit_search_json,
    parse_x_search_html,
    post_text,
)


def test_classify_quotes_buckets_correctly():
    quotes = [
        "Tombstone is amazing, completely destroyed the competition!",
        "What a boring fight, Tombstone looked weak today.",
        "It was a fight.",
    ]
    counts = classify_quotes(quotes)
    assert counts["positive"] == 1
    assert counts["negative"] == 1
    assert counts["neutral"] == 1


def test_classify_posts_buckets_structured_posts():
    posts = [
        {"title": "Tombstone is amazing", "body": "completely destroyed"},
        {"title": "boring fight", "body": "looked weak today"},
        {"title": "It was a fight.", "body": None},
    ]
    counts = classify_posts(posts)
    assert counts["positive"] == 1
    assert counts["negative"] == 1
    assert counts["neutral"] == 1
    assert posts[0]["sentiment"] == "positive"


def test_parse_reddit_search_json_extracts_structured_posts():
    payload = json.dumps(
        {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "abc1",
                            "title": "Tombstone is back",
                            "selftext": "Excited to see them again",
                            "permalink": "/r/battlebots/comments/abc1/title/",
                            "score": 12,
                            "num_comments": 3,
                            "subreddit": "battlebots",
                            "created_utc": 1_700_000_000,
                        }
                    },
                    {
                        "data": {
                            "title": "Match recap",
                            "selftext": "",
                        }
                    },
                    {
                        "data": {
                            "title": "",
                            "selftext": "Body only post",
                        }
                    },
                ]
            }
        }
    )
    posts = parse_reddit_search_json(payload, max_quotes=10)
    assert len(posts) == 3
    assert posts[0]["title"] == "Tombstone is back"
    assert posts[0]["body"] == "Excited to see them again"
    assert posts[0]["url"] == "https://www.reddit.com/r/battlebots/comments/abc1/title/"
    assert posts[0]["score"] == 12
    assert "Tombstone is back" in post_text(posts[0])
    assert posts[1]["title"] == "Match recap"
    assert posts[2]["body"] == "Body only post"


def test_parse_reddit_search_json_respects_max_quotes():
    payload = json.dumps(
        {
            "data": {
                "children": [
                    {"data": {"title": f"post {i}"}} for i in range(20)
                ]
            }
        }
    )
    posts = parse_reddit_search_json(payload, max_quotes=5)
    assert len(posts) == 5


def test_parse_reddit_search_json_handles_invalid_payload():
    assert parse_reddit_search_json("not json", max_quotes=10) == []


X_HTML = """
<html><body>
  <article>
    <div data-testid="tweetText">Tombstone vs HUGE was insane!!! best fight ever</div>
  </article>
  <article>
    <div data-testid="tweetText">Honestly underwhelming match tbh</div>
  </article>
  <article>
    <p>Some unrelated long-ish content that has nothing to do with bots really</p>
  </article>
</body></html>
"""


def test_parse_x_search_html_pulls_tweet_text():
    posts = parse_x_search_html(X_HTML, max_quotes=10)
    texts = [post_text(p) for p in posts]
    assert any("insane" in t.lower() for t in texts)
    assert any("underwhelming" in t.lower() for t in texts)


def test_parse_reddit_search_json_sorts_by_recency_and_dedupes():
    older = {
        "id": "old1",
        "title": "Old discussion",
        "selftext": "from a while ago",
        "created_utc": 1_700_000_000,
        "score": 10,
        "num_comments": 2,
        "subreddit": "battlebots",
    }
    newer = {
        "id": "new1",
        "title": "Fresh hot take",
        "selftext": "just streamed live",
        "created_utc": 1_900_000_000,
        "score": 99,
        "num_comments": 47,
        "subreddit": "battlebots",
    }
    duplicate_of_newer = {**newer}

    payload = json.dumps(
        {
            "data": {
                "children": [
                    {"data": older},
                    {"data": newer},
                    {"data": duplicate_of_newer},
                ]
            }
        }
    )

    posts = parse_reddit_search_json(payload, max_quotes=10)
    assert len(posts) == 2, "Posts with the same id should be deduped"
    assert posts[0]["title"] == "Fresh hot take"
    assert posts[0]["created_at"] == "2030-03-17"
    assert posts[1]["title"] == "Old discussion"


def test_parse_reddit_search_json_can_omit_metadata_prefix():
    payload = json.dumps(
        {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "abc",
                            "title": "Match recap",
                            "selftext": "stuff happened",
                            "created_utc": 1_700_000_000,
                            "score": 5,
                            "subreddit": "battlebots",
                        }
                    }
                ]
            }
        }
    )
    posts = parse_reddit_search_json(
        payload, max_quotes=5, include_metadata=False
    )
    assert post_text(posts[0]) == "Match recap — stuff happened"
    assert not posts[0]["text"].startswith("[")


def test_normalize_posts_converts_legacy_strings():
    posts = normalize_posts(["[2024-01-01 · 5↑ · 2 comments · r/battlebots] Old quote"])
    assert len(posts) == 1
    assert posts[0]["title"].startswith("[2024-01-01")
    assert posts[0]["sentiment"] in {"positive", "negative", "neutral"}


REDDIT_COMMENTS_PAYLOAD = """
[
  {"data": {"children": [{"kind": "t3", "data": {"id": "post1"}}]}},
  {
    "data": {
      "children": [
        {
          "kind": "t1",
          "data": {
            "id": "cmt1",
            "body": "Tombstone's weapon is terrifying — best in the field.",
            "score": 15,
            "created_utc": 1700000000,
            "subreddit": "battlebots",
            "permalink": "/r/battlebots/comments/post1/x/cmt1/"
          }
        },
        {"kind": "more", "data": {}}
      ]
    }
  }
]
"""


def test_parse_reddit_comments_json_extracts_comment_bodies():
    from backend.scrapers.parsers.sentiment_parser import parse_reddit_comments_json

    comments = parse_reddit_comments_json(
        REDDIT_COMMENTS_PAYLOAD, post_id="post1", max_comments=5
    )
    assert len(comments) == 1
    assert comments[0]["type"] == "comment"
    assert comments[0]["parent_id"] == "post1"
    assert "terrifying" in comments[0]["body"]
    assert comments[0]["score"] == 15
