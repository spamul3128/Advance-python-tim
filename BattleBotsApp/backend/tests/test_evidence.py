"""Tests for evidence catalog and confidence refinement."""

from backend.ai.evidence import build_evidence_catalog, refine_confidence


def test_build_evidence_catalog_assigns_ids_and_urls():
    facts = build_evidence_catalog(
        bot_a={
            "name": "Tombstone",
            "weapon_type": "Horizontal spinner",
            "source_url": "https://battlebots.fandom.com/wiki/Tombstone",
        },
        bot_b={"name": "HUGE", "weapon_type": "Vertical spinner"},
        history_a=[
            {
                "opponent_name": "Bite Force",
                "won": True,
                "method": "KO",
                "season": "Season 3",
                "round": "Final",
                "source_url": "https://battlebots.fandom.com/wiki/Tombstone_vs_Bite_Force",
            }
        ],
        history_b=[],
        sentiment_a=[
            {
                "source": "reddit",
                "positive_count": 2,
                "negative_count": 0,
                "neutral_count": 1,
                "sample_quotes": [
                    {
                        "title": "Tombstone hype",
                        "body": "Best bot ever",
                        "url": "https://reddit.com/r/battlebots/comments/abc",
                    }
                ],
            }
        ],
        sentiment_b=[],
    )
    assert facts[0]["id"] == "F001"
    assert any(f["category"] == "match" for f in facts)
    assert any(f.get("source_url") and "reddit.com" in f["source_url"] for f in facts)


def test_refine_confidence_penalizes_sparse_data():
    low = refine_confidence(
        0.72,
        winner_name="A",
        bot_a_name="A",
        bot_b_name="B",
        history_a=[{"won": True}],
        history_b=[],
        facts=[{"id": "F001"}],
    )
    assert low < 0.72
    assert low != 0.7
    assert round(low, 3) == low
