"""Smoke tests for schema initialization and repository upserts."""

from __future__ import annotations

from backend.db.repositories import (
    BotRepository,
    MatchRepository,
    PredictionRepository,
    SentimentRepository,
)


def test_schema_creates_expected_tables(tmp_db):
    rows = tmp_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    names = {r["name"] for r in rows}
    assert {"bots", "matches", "sentiment", "predictions"}.issubset(names)


def test_bot_upsert_is_idempotent(tmp_db):
    repo = BotRepository(tmp_db)
    bot_id = repo.upsert(
        {
            "name": "Tombstone",
            "weight_class": "Heavyweight",
            "weapon_type": "Spinning bar",
            "team_name": "Hardcore Robotics",
            "country": "USA",
            "image_url": None,
            "description": "Iconic horizontal spinner.",
            "weapon_description": "Steel bar",
            "source_url": "https://example.com/tombstone",
        }
    )
    again = repo.upsert(
        {
            "name": "Tombstone",
            "weight_class": "Heavyweight",
            "weapon_type": "Spinning bar (updated)",
            "team_name": "Hardcore Robotics",
            "country": "USA",
            "image_url": None,
            "description": "Iconic horizontal spinner.",
            "weapon_description": "Steel bar",
            "source_url": "https://example.com/tombstone",
        }
    )
    assert bot_id == again
    row = repo.get_by_name("Tombstone")
    assert row is not None
    assert row["weapon_type"] == "Spinning bar (updated)"
    assert repo.count() == 1


def test_match_upsert_resolves_unique_constraint(tmp_db):
    bot_repo = BotRepository(tmp_db)
    a = bot_repo.upsert({"name": "Tombstone"})
    b = bot_repo.upsert({"name": "HUGE"})

    match_repo = MatchRepository(tmp_db)
    match_repo.upsert(
        {
            "bot_a_id": a,
            "bot_b_id": b,
            "winner_id": a,
            "method": "KO",
            "season": "World Championship VIII",
            "round": "Round of 32",
            "episode": "Episode 3",
        }
    )
    # Same key again should update, not duplicate.
    match_repo.upsert(
        {
            "bot_a_id": a,
            "bot_b_id": b,
            "winner_id": b,
            "method": "JD",
            "season": "World Championship VIII",
            "round": "Round of 32",
            "episode": "Episode 3",
        }
    )
    assert match_repo.count() == 1
    rows = match_repo.list_for_bot(a)
    assert len(rows) == 1
    assert rows[0]["method"] == "JD"
    assert rows[0]["winner_id"] == b


def test_sentiment_upsert_stores_quotes_as_json(tmp_db):
    bot_id = BotRepository(tmp_db).upsert({"name": "Hydra"})
    repo = SentimentRepository(tmp_db)
    repo.upsert(
        bot_id=bot_id,
        source="reddit",
        positive_count=4,
        negative_count=1,
        neutral_count=2,
        sample_quotes=["Hydra is amazing", "Hydra flips everyone"],
    )

    rows = repo.list_for_bot(bot_id)
    assert len(rows) == 1
    assert rows[0]["positive_count"] == 4
    posts = rows[0]["sample_quotes"]
    assert len(posts) == 2
    assert posts[0]["title"] == "Hydra is amazing"
    assert posts[1]["title"] == "Hydra flips everyone"


def test_prediction_upsert_replaces_cached_record(tmp_db):
    bot_repo = BotRepository(tmp_db)
    a = bot_repo.upsert({"name": "Tombstone"})
    b = bot_repo.upsert({"name": "HUGE"})

    repo = PredictionRepository(tmp_db)
    repo.upsert(
        bot_a_id=a,
        bot_b_id=b,
        winner_prediction=a,
        confidence=0.7,
        scouting_report="First report",
        model="test-model",
    )
    repo.upsert(
        bot_a_id=a,
        bot_b_id=b,
        winner_prediction=b,
        confidence=0.55,
        scouting_report="Updated report",
        model="test-model",
    )

    row = repo.get_for_pair(a, b)
    assert row is not None
    assert row["scouting_report"] == "Updated report"
    assert row["winner_prediction"] == b
