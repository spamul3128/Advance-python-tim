"""Tests for the Fandom match-table + career-log parsers."""

from __future__ import annotations

from backend.scrapers.parsers.matches_parser import (
    parse_career_log,
    parse_match_tables,
)


FANDOM_TOURNAMENT_HTML = """
<html><body>
  <div class="mw-parser-output">
    <h2>Round of 32</h2>
    <table class="wikitable">
      <tr><th>Robot 1</th><th>Robot 2</th><th>Winner</th><th>Method</th></tr>
      <tr>
        <td>Tombstone</td>
        <td>HUGE</td>
        <td>Tombstone</td>
        <td>KO at 1:32</td>
      </tr>
      <tr>
        <td>Witch Doctor</td>
        <td>End Game</td>
        <td>End Game</td>
        <td>Judges' decision</td>
      </tr>
    </table>

    <h3>Episode 5</h3>
    <table class="wikitable">
      <tr><th>Competitor</th><th>Competitor</th><th>Result</th></tr>
      <tr>
        <td>Hydra</td>
        <td>Minotaur</td>
        <td>Hydra by TKO</td>
      </tr>
    </table>

    <h2>Unrelated section</h2>
    <table class="wikitable">
      <tr><th>Score</th><th>Rank</th></tr>
      <tr><td>10</td><td>1</td></tr>
    </table>
  </div>
</body></html>
"""


def test_parse_match_tables_extracts_competitors_and_winners():
    matches = parse_match_tables(
        FANDOM_TOURNAMENT_HTML,
        season="World Championship VIII",
        source_url="https://battlebots.fandom.com/wiki/World_Championship_VIII",
    )
    assert len(matches) == 3

    tombstone_match = next(m for m in matches if m["bot_a_name"] == "Tombstone")
    assert tombstone_match["bot_b_name"] == "HUGE"
    assert tombstone_match["winner_name"] == "Tombstone"
    assert tombstone_match["method"] == "KO"
    assert tombstone_match["round"] == "Round of 32"
    assert tombstone_match["season"] == "World Championship VIII"

    wd_match = next(m for m in matches if m["bot_a_name"] == "Witch Doctor")
    assert wd_match["winner_name"] == "End Game"
    assert wd_match["method"] == "JD"

    hydra_match = next(m for m in matches if m["bot_a_name"] == "Hydra")
    assert hydra_match["bot_b_name"] == "Minotaur"
    assert hydra_match["winner_name"] == "Hydra"
    assert hydra_match["method"] == "TKO"
    # Episode heading was h3 between the two tables.
    assert hydra_match["episode"] == "Episode 5"


def test_parse_match_tables_ignores_non_match_tables():
    matches = parse_match_tables(FANDOM_TOURNAMENT_HTML)
    # The "Score / Rank" table should have been filtered out.
    for m in matches:
        assert m["bot_a_name"] not in ("10",)


# ---------------------------------------------------------------------------
# Career-log parser — exercises the real-world Fandom structure.
# ---------------------------------------------------------------------------

CAREER_LOG_HTML = """
<html><body>
  <table class="article-table">
    <tr><th>World Championship I [ ]</th></tr>
    <tr>
      <td>
        Tombstone vs <a href="/wiki/Bronco">Bronco</a>
        In the semi-final, Tombstone defeated Bronco by KO at 2:14.
      </td>
    </tr>
    <tr>
      <td>
        Tombstone vs <a href="/wiki/Inertia_Labs">Inertia Labs</a>
        <a href="/wiki/Bite_Force">Bite Force</a>
        In the championship final, Tombstone was eliminated by Bite Force in a unanimous decision.
      </td>
    </tr>
    <tr><th>World Championship II [ ]</th></tr>
    <tr>
      <td>
        Tombstone vs <a href="/wiki/HUGE">HUGE</a>
        Tombstone won by TKO after damaging HUGE's weapon system.
      </td>
    </tr>
    <tr>
      <td>
        Tombstone vs <a href="/wiki/Some_Driver">Donald Hutson</a>
        <a href="/wiki/Witch_Doctor">Witch Doctor</a>
        Witch Doctor defeated Tombstone in the quarter-finals.
      </td>
    </tr>
  </table>
</body></html>
"""


def test_parse_career_log_prefers_known_bot_anchors():
    known = {"Tombstone", "Bronco", "Bite Force", "HUGE", "Witch Doctor"}
    rows = parse_career_log(
        CAREER_LOG_HTML, bot_name="Tombstone", known_bot_names=known
    )
    assert len(rows) == 4

    by_opponent = {row["bot_b_name"]: row for row in rows}
    # Inertia Labs (team) must not be picked as the opponent — Bite Force is the bot.
    assert "Inertia Labs" not in by_opponent
    assert "Donald Hutson" not in by_opponent
    assert {"Bronco", "Bite Force", "HUGE", "Witch Doctor"} <= set(by_opponent)


def test_parse_career_log_extracts_winner_and_method():
    known = {"Tombstone", "Bronco", "Bite Force", "HUGE", "Witch Doctor"}
    rows = parse_career_log(
        CAREER_LOG_HTML, bot_name="Tombstone", known_bot_names=known
    )
    by_opponent = {row["bot_b_name"]: row for row in rows}

    assert by_opponent["Bronco"]["winner_name"] == "Tombstone"
    assert by_opponent["Bronco"]["method"] == "KO"

    assert by_opponent["Bite Force"]["winner_name"] == "Bite Force"
    assert by_opponent["Bite Force"]["method"] == "JD"

    assert by_opponent["HUGE"]["winner_name"] == "Tombstone"
    assert by_opponent["HUGE"]["method"] == "TKO"

    assert by_opponent["Witch Doctor"]["winner_name"] == "Witch Doctor"


def test_parse_career_log_assigns_section_as_season():
    known = {"Tombstone", "Bronco", "Bite Force", "HUGE", "Witch Doctor"}
    rows = parse_career_log(
        CAREER_LOG_HTML, bot_name="Tombstone", known_bot_names=known
    )
    by_opponent = {row["bot_b_name"]: row for row in rows}
    assert by_opponent["Bronco"]["season"] == "World Championship I"
    assert by_opponent["HUGE"]["season"] == "World Championship II"


# ---------------------------------------------------------------------------
# Winner-inference regression coverage. These templates mirror real Fandom
# recap phrasings that were missed by earlier heuristics.
# ---------------------------------------------------------------------------


def _build_single_row_html(recap: str, *, page_owner: str, opponent: str) -> str:
    """Wrap a recap in the minimum Fandom-shaped career-log HTML."""
    opp_slug = opponent.replace(" ", "_")
    return (
        f"<html><body><table class=\"article-table\">"
        f"<tr><th>World Championship I [ ]</th></tr>"
        f"<tr><th>World Championship I [ ]</th></tr>"
        f"<tr><th>World Championship I [ ]</th></tr>"
        f"<tr><td>{page_owner} vs <a href=\"/wiki/{opp_slug}\">{opponent}</a>"
        f" {recap}</td></tr>"
        f"<tr><td>{page_owner} vs <a href=\"/wiki/{opp_slug}\">{opponent}</a>"
        f" filler.</td></tr>"
        f"<tr><td>{page_owner} vs <a href=\"/wiki/{opp_slug}\">{opponent}</a>"
        f" filler.</td></tr>"
        f"</table></body></html>"
    )


_WINNER_INFERENCE_CASES = (
    # (recap, page_owner, opponent, expected_winner)
    (
        "giving Tombstone the win by TKO and advancing to the next round.",
        "Tombstone",
        "Mer Madd",
        "Tombstone",
    ),
    (
        "Tombstone again won by knockout after 43 seconds.",
        "Tombstone",
        "Vault",
        "Tombstone",
    ),
    (
        "Tombstone was eliminated after a total match time of 43 seconds, "
        "with official BattleBots records listing it as having gone to "
        "judges' decision.",
        "Tombstone",
        "VD6.0",
        "VD6.0",
    ),
    (
        "ultimately winning the match by knockout after one minute and "
        "32 seconds.",
        "Tombstone",
        "Megabyte",
        "Tombstone",
    ),
    (
        "the Judges unanimously voted for Bite Force, giving Team Aptyx "
        "Designs their first win.",
        "Bite Force",
        "Warhead",
        "Bite Force",
    ),
    (
        "the Judges deemed Bite Force's start and finish strong enough to "
        "hand it the victory unanimously, putting Bite Force at 1-0 and "
        "giving it the first win of the season.",
        "Bite Force",
        "Blacksmith",
        "Bite Force",
    ),
    (
        "this was enough to finally put an end to the 11th seed and send "
        "Bite Force to the Semi-Finals for the second time in three seasons.",
        "Bite Force",
        "ROTATOR",
        "Bite Force",
    ),
    (
        "The Judges awarded Bite Force a unanimous 3-0 decision.",
        "Bite Force",
        "Yeti",
        "Bite Force",
    ),
    (
        "After careful consideration of the fight, the judges ultimately "
        "scored the match unanimously in favor of Bite Force, confirming a "
        "runner-up finish for Hardcore Robotics and Tombstone.",
        "Tombstone",
        "Bite Force",
        "Bite Force",
    ),
)


def test_infer_winner_handles_real_fandom_phrasings():
    """Each recap below mirrors a real Fandom phrasing that previously
    failed to resolve a winner. The parser must now classify them correctly."""
    failures: list[str] = []
    for recap, owner, opp, expected in _WINNER_INFERENCE_CASES:
        html = _build_single_row_html(recap, page_owner=owner, opponent=opp)
        rows = parse_career_log(html, bot_name=owner, known_bot_names={owner, opp})
        if not rows:
            failures.append(f"no rows parsed for {owner} vs {opp}")
            continue
        actual = rows[0]["winner_name"]
        if actual != expected:
            failures.append(
                f"{owner} vs {opp}: expected {expected!r}, got {actual!r}"
            )
    assert not failures, "\n".join(failures)


def test_infer_winner_returns_none_on_ambiguous_recap():
    """A recap with no win/loss signal must stay unresolved (no false positives)."""
    recap = "Both robots traded blows for the full three minutes."
    html = _build_single_row_html(recap, page_owner="Tombstone", opponent="Minotaur")
    rows = parse_career_log(html, bot_name="Tombstone", known_bot_names={"Tombstone", "Minotaur"})
    assert rows
    assert rows[0]["winner_name"] is None
