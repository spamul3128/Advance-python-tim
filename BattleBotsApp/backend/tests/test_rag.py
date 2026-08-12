"""Tests for RAG utilities."""

from __future__ import annotations

from backend.ai.rag import cosine_similarity, posts_to_chunk_records


def test_cosine_similarity_identical_vectors():
    vec = [1.0, 0.0, 0.0]
    assert cosine_similarity(vec, vec) == 1.0


def test_cosine_similarity_orthogonal_vectors():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_posts_to_chunk_records_flattens_posts_and_comments():
    posts = [
        {
            "id": "p1",
            "type": "post",
            "title": "Tombstone dominates again",
            "body": "That horizontal spinner is unstoppable in the arena.",
            "url": "https://reddit.com/p1",
            "score": 42,
            "subreddit": "battlebots",
        },
        {
            "id": "c1",
            "type": "comment",
            "parent_id": "p1",
            "body": "Agreed — best weapon in the field right now for sure.",
            "url": "https://reddit.com/c1",
            "score": 10,
            "subreddit": "battlebots",
        },
    ]
    records = posts_to_chunk_records(posts)
    assert len(records) == 2
    assert records[0]["external_id"] == "p1"
    assert records[1]["external_id"] == "p1:c1"
    assert records[1]["chunk_type"] == "comment"
