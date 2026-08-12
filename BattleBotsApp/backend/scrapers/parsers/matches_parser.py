"""Parser for match-history tables on the BattleBots Fandom wiki.

Each season has a tournament page (e.g. `World_Championship_VIII`) containing
multiple `<table class="wikitable">` blocks. We're interested in tables whose
header row mentions both "Robot" / "vs" / "Result" / "Winner" — i.e. fight
result tables.

Returned dicts use bot *names* (strings), not ids — the scraper resolves them
to bot ids against the local DB before persistence.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

# Method classification. Order matters: more specific patterns must come
# before their substrings (TKO before KO; JD before plain "decision").
# Each entry is (canonical_label, regex pattern) — patterns use word
# boundaries so "ko" doesn't match inside "tko".
_METHOD_PATTERNS: tuple[tuple[str, str], ...] = (
    ("TKO", r"\btko\b"),
    ("KO", r"\b(ko|knock\s*-?\s*out)\b"),
    ("JD", r"\b(jd|judges?|decision)\b"),
    ("SUB", r"\b(submission|tap[-\s]?out)\b"),
)


def parse_match_tables(
    html: str,
    *,
    season: str | None = None,
    source_url: str | None = None,
) -> list[dict[str, Any]]:
    """Extract match rows from a Fandom tournament page.

    Returns a list of dicts with the shape::

        {
            "bot_a_name": "Tombstone",
            "bot_b_name": "HUGE",
            "winner_name": "Tombstone" | None,
            "method": "KO" | "JD" | None,
            "season": "World Championship VIII",
            "episode": "Episode 3" | None,
            "round": "Round of 32" | None,
            "source_url": "...",
        }
    """
    soup = BeautifulSoup(html, "lxml")
    matches: list[dict[str, Any]] = []

    # Track the most recent section heading so we can use it as "round".
    current_round: str | None = None
    current_episode: str | None = None

    for element in soup.select(".mw-parser-output > *"):
        if element.name in {"h2", "h3", "h4"}:
            heading = element.get_text(" ", strip=True)
            if _looks_like_episode(heading):
                current_episode = heading
            else:
                current_round = heading
            continue

        if element.name != "table":
            # Tables can also be nested in divs on some pages.
            for nested in element.find_all("table"):
                matches.extend(
                    _parse_single_table(
                        nested,
                        season=season,
                        episode=current_episode,
                        round_label=current_round,
                        source_url=source_url,
                    )
                )
            continue

        matches.extend(
            _parse_single_table(
                element,
                season=season,
                episode=current_episode,
                round_label=current_round,
                source_url=source_url,
            )
        )

    return matches


def _looks_like_episode(text: str) -> bool:
    return bool(re.search(r"\bepisode\b", text, flags=re.IGNORECASE))


def _parse_single_table(
    table: Tag,
    *,
    season: str | None,
    episode: str | None,
    round_label: str | None,
    source_url: str | None,
) -> list[dict[str, Any]]:
    header_cells = table.find_all("th")
    if not header_cells:
        return []

    headers = [th.get_text(" ", strip=True).lower() for th in header_cells]
    if not _is_match_table(headers):
        return []

    col_indexes = _resolve_columns(headers)

    rows: list[dict[str, Any]] = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if len(cells) < 2 or tr.find("th") is not None and not tr.find("td"):
            # Header row.
            continue

        try:
            bot_a, bot_b = _extract_competitors(cells, col_indexes)
        except ValueError:
            continue

        if not bot_a or not bot_b:
            continue

        winner_text = _cell_text(cells, col_indexes.get("winner"))
        method_text = _cell_text(cells, col_indexes.get("method"))
        result_text = _cell_text(cells, col_indexes.get("result"))

        # If there's no dedicated winner column, the result column often
        # encodes both the winner and the method (e.g. "Hydra by TKO").
        winner_name = _resolve_winner(winner_text or result_text, bot_a, bot_b)
        method = _normalize_method(method_text or result_text or winner_text)

        rows.append(
            {
                "bot_a_name": bot_a,
                "bot_b_name": bot_b,
                "winner_name": winner_name,
                "method": method,
                "season": season,
                "episode": episode,
                "round": round_label,
                "source_url": source_url,
            }
        )

    return rows


def _is_match_table(headers: list[str]) -> bool:
    joined = " ".join(headers)
    has_bots = any(k in joined for k in ("robot", "competitor", "bot"))
    has_outcome = any(k in joined for k in ("winner", "result", "outcome", "method"))
    return has_bots and has_outcome


def _resolve_columns(headers: list[str]) -> dict[str, int]:
    """Map canonical column names to their index in the row."""
    mapping: dict[str, int] = {}
    for idx, header in enumerate(headers):
        if "winner" in header and "winner" not in mapping:
            mapping["winner"] = idx
        elif "method" in header and "method" not in mapping:
            mapping["method"] = idx
        elif "result" in header and "result" not in mapping:
            mapping["result"] = idx
        elif any(k in header for k in ("robot", "competitor", "bot")):
            mapping.setdefault("bot_a", idx)
            # If we already have bot_a, the next match becomes bot_b.
            if mapping.get("bot_a") != idx:
                mapping.setdefault("bot_b", idx)
    return mapping


def _extract_competitors(
    cells: list[Tag], col_indexes: dict[str, int]
) -> tuple[str, str]:
    """Return (bot_a, bot_b). Supports both 2-column and 'A vs B' single-cell layouts."""
    if "bot_a" in col_indexes and "bot_b" in col_indexes:
        a = _clean_cell(cells[col_indexes["bot_a"]])
        b = _clean_cell(cells[col_indexes["bot_b"]])
        return a, b

    # Fall back: look for a cell whose text contains " vs " or " VS ".
    for cell in cells:
        text = cell.get_text(" ", strip=True)
        if re.search(r"\bvs\.?\b", text, flags=re.IGNORECASE):
            parts = re.split(r"\s+vs\.?\s+", text, flags=re.IGNORECASE)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()

    raise ValueError("Could not identify two competitors in row.")


def _cell_text(cells: list[Tag], idx: int | None) -> str | None:
    if idx is None or idx >= len(cells):
        return None
    return cells[idx].get_text(" ", strip=True) or None


def _clean_cell(cell: Tag) -> str:
    """Strip footnote markers like [1] and bracketed annotations."""
    text = cell.get_text(" ", strip=True)
    text = re.sub(r"\[\d+\]", "", text)
    return text.strip()


def _resolve_winner(
    winner_text: str | None, bot_a: str, bot_b: str
) -> str | None:
    if not winner_text:
        return None
    lower = winner_text.lower()
    if bot_a.lower() in lower:
        return bot_a
    if bot_b.lower() in lower:
        return bot_b
    return None


def _normalize_method(text: str | None) -> str | None:
    """Return canonical method label (KO/TKO/JD/SUB) or None.

    Patterns are checked in order so TKO wins over KO, etc.
    """
    if not text:
        return None
    lower = text.lower()
    for label, pattern in _METHOD_PATTERNS:
        if re.search(pattern, lower):
            return label
    return None


# ---------------------------------------------------------------------------
# Career fight log parser (per-bot Fandom page)
#
# Tournament pages don't actually carry per-fight results for most seasons —
# the fight metadata lives on each *bot's* wiki page, in an `article-table`
# that lists every match the bot has competed in, grouped by tournament.
#
# Layout (Tombstone is the example):
#
#   <table class="article-table">
#     <tr><th>World Championship I [ ]</th></tr>     ← section header
#     <tr><td>Tombstone vs Bronco Advancing to the final four, ...</td></tr>
#     <tr><td>Tombstone vs Bite Force In the championship final, ...</td></tr>
#     ...
#
# Each <td> contains a single anchor pointing to the opponent's wiki page,
# followed by a free-text recap of the fight. We use the anchor to identify
# the opponent and apply heuristics to the recap to recover winner/method.
# ---------------------------------------------------------------------------

# Keyword sets used by the final fallback after explicit patterns fail.
# These are intentionally narrow — they only fire when no other pattern
# pinpoints a winner, so false positives bias toward "unknown" rather
# than a wrong-but-confident answer.
_WIN_SIGNALS: tuple[str, ...] = (
    "won the match",
    "won the fight",
    "won by",
    "winning the match",
    "winning the fight",
    "win by ko",
    "win by tko",
    "win by judges",
    "the win by",
    "secured the win",
    "claimed the win",
    "took the win",
    "earned the win",
)

_LOSS_SIGNALS: tuple[str, ...] = (
    "was eliminated",
    "got eliminated",
    "this loss",
    "the loss",
    "championship loss",
    "loss consigned",
    "loss meant",
    "counted out",
    "knocked out and eliminated",
    "sent home",
)


# Adverbs we allow between the subject (bot name) and the verb. Keeping
# this list narrow (vs. arbitrary `\w+`) prevents passive constructions
# like "Tombstone was eliminated" from being mis-parsed as an active win.
_SAFE_ADVERBS = (
    r"(?:then|finally|narrowly|again|just|now|quickly|easily|ultimately|"
    r"swiftly|already|repeatedly|nonetheless|however|also|too|once|"
    r"eventually|surprisingly|barely|here|next)"
)
_OPT_ADVERB = rf"(?:\s+{_SAFE_ADVERBS}){{0,2}}"

# Negative lookahead that filters out passive constructions for verbs
# that can be either active or passive. Without this, "Tombstone was
# eliminated" would be misread as Tombstone defeating something.
_PASSIVE_GUARD = r"(?!\s+(?:was|were|got|is|been|had\s+been|gets|seemed|appeared)\b)"


def _build_win_patterns(bot_re: str, opp_re: str) -> tuple[str, ...]:
    """Compose the win-detecting regexes for a specific bot pair.

    Returns a tuple of pattern strings whose first capture group, when
    matched, identifies the *winner* of the fight (in lowercase form).
    """
    pair = f"({bot_re}|{opp_re})"
    return (
        # "Tombstone won by KO" / "Tombstone again won by judges"
        rf"\b{pair}{_OPT_ADVERB}\s+won\s+(?:by|via|the|in|after)\b",
        # "Tombstone defeated Bronco" — active voice only, requires an object.
        rf"\b{pair}{_PASSIVE_GUARD}{_OPT_ADVERB}\s+(?:defeated|knocked\s+out|destroyed|eliminated|dispatched|dismantled|smashed|obliterated|crushed|overpowered|outlasted)\s+\w",
        # "giving Tombstone the win" — extremely common Fandom phrasing.
        rf"\bgiving\s+{pair}\s+the\s+(?:win|victory)\b",
        # "voted for Bite Force" / "voted unanimously in favor of Bite Force"
        rf"\bvoted\s+(?:unanimously\s+)?(?:in\s+favor\s+of\s+|for\s+){pair}\b",
        # "awarded Bite Force the/a (decision|win|victory|3-0)"
        rf"\b(?:awarded|granted|gave|handed)\s+{pair}\s+(?:a|the)\s+(?:unanimous\s+|split\s+)?(?:\d[-\u2013]\d\s+)?(?:win|victory|decision|judges?)\b",
        # "hand it the victory" — pronoun version, only fires alongside the
        # named-bot pattern above so it's safe.
        rf"\bhand(?:ed|s)?\s+(?:it|them)\s+the\s+(?:win|victory|decision)\b.*?{pair}",
        # "send Bite Force to the Semi-Finals" — implies advancement.
        rf"\bsen[dt](?:ing|s)?\s+{pair}\s+(?:to|on\s+to|through\s+to)\s+(?:the\s+)?(?:semi-?finals?|finals?|quarter-?finals?|championship|round\s+of|next\s+round|final\s+four)\b",
        rf"\b{pair}\s+(?:was|were)\s+(?:declared|crowned|named|awarded)\s+(?:the\s+)?(?:winner|victor|victory)\b",
        rf"\b{pair}\s+(?:secured|claimed|took|earned)\s+the\s+(?:win|victory|knockout)\b",
        rf"\bdeclared\s+{pair}\s+the\s+(?:winner|victor)\b",
        rf"\bthe\s+(?:win|victory)\s+(?:went\s+to|belonged\s+to)\s+{pair}\b",
        rf"\bin\s+favor\s+of\s+{pair}\b",
        rf"\b{pair}'s\s+(?:victory|win|dominant\s+win)\b",
        rf"\bwinner(?:\s+is|\s+was|:)?\s+{pair}\b",
        rf"\b{pair}\s+advanced\s+(?:to|past|after\s+winning)\b",
        # "Bite Force a unanimous 3-0 decision"
        rf"\b{pair}\s+(?:a|the)\s+(?:unanimous\s+|split\s+)?\d[-\u2013]\d\s+(?:decision|judges?)\b",
    )


def _build_loss_patterns(bot_re: str, opp_re: str) -> tuple[str, ...]:
    """Compose regexes that, when matched, identify the *loser*.

    The match's capture group is the LOSER's lowercase name; the caller
    returns the opponent as the winner.
    """
    pair = f"({bot_re}|{opp_re})"
    return (
        rf"\b{pair}\s+(?:was|were|got|is)\s+(?:defeated|eliminated|knocked\s+out|destroyed|dispatched|dismantled|sent\s+home|counted\s+out|crushed)\b",
        rf"\b{pair}{_OPT_ADVERB}\s+lost\s+(?:to|the|via|by)\b",
        rf"\b{pair}\s+suffered\s+(?:a|the|its|an?)\s+(?:loss|defeat|elimination)\b",
        rf"\bloss\s+(?:for|consigned|meant\s+(?:that\s+)?)\s*{pair}\b",
        rf"\beliminating\s+{pair}\b",
        rf"\bdefeated\s+{pair}\b",
        rf"\bdestroyed\s+{pair}\b",
        rf"\bknocked\s+out\s+{pair}\b",
    )


def parse_career_log(
    html: str,
    *,
    bot_name: str,
    known_bot_names: set[str] | None = None,
    source_url: str | None = None,
) -> list[dict[str, Any]]:
    """Parse the career-fights table on a bot's Fandom page.

    `bot_name` is the page owner. `known_bot_names` is the set of bot names
    currently in our DB; used to disambiguate opponents when the recap text
    mentions multiple bots.

    Returns the same dict shape as `parse_match_tables` so the caller can
    upsert with the existing repository code.
    """
    soup = BeautifulSoup(html, "lxml")
    known_lower: dict[str, str] = {}
    if known_bot_names:
        known_lower = {n.lower(): n for n in known_bot_names if n}

    target_table = _find_career_table(soup, bot_name)
    if target_table is None:
        return []

    matches: list[dict[str, Any]] = []
    current_section: str | None = None

    for tr in target_table.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue

        # A row with only a <th> and a single cell is a section header
        # carrying the tournament name.
        if all(c.name == "th" for c in cells) and len(cells) == 1:
            current_section = _clean_section_label(cells[0].get_text(" ", strip=True))
            continue

        # Some tables put header text in a <td colspan="...">; treat
        # single-cell rows with no opponent link as section headers too.
        cell = cells[0]
        text = cell.get_text(" ", strip=True)
        if not text or not re.search(r"\bvs\.?\b", text, flags=re.IGNORECASE):
            continue

        opponent = _identify_opponent(cell, bot_name=bot_name, known_lower=known_lower)
        if not opponent:
            continue
        # Skip self-references (some pages contain odd internal links).
        if opponent.lower() == bot_name.lower():
            continue

        recap = _strip_matchup_prefix(text, bot_name=bot_name, opponent=opponent)
        winner = _infer_winner(recap, bot_name=bot_name, opponent=opponent)
        method = _normalize_method(recap)

        matches.append(
            {
                "bot_a_name": bot_name,
                "bot_b_name": opponent,
                "winner_name": winner,
                "method": method,
                "season": current_section,
                "episode": None,
                "round": None,
                "source_url": source_url,
            }
        )

    return matches


def _find_career_table(soup: BeautifulSoup, bot_name: str) -> Tag | None:
    """Locate the per-bot career fight log table on a Fandom bot page.

    Heuristic: an `article-table` whose body has at least three rows whose
    text starts with `<bot_name> vs ...`.
    """
    candidates = soup.find_all("table")
    best: Tag | None = None
    best_score = 0
    bot_lower = bot_name.lower()

    for table in candidates:
        score = 0
        for tr in table.find_all("tr"):
            text = tr.get_text(" ", strip=True).lower()
            if text.startswith(f"{bot_lower} vs"):
                score += 1
        if score >= 3 and score > best_score:
            best = table
            best_score = score
    return best


def _clean_section_label(text: str) -> str:
    """Drop the ` [ ]` edit-link suffix Fandom appends to section headers."""
    return re.sub(r"\s*\[\s*\]\s*$", "", text).strip()


def _identify_opponent(
    cell: Tag, *, bot_name: str, known_lower: dict[str, str]
) -> str | None:
    """Pick the opponent name out of a row.

    Multiple `<a href="/wiki/...">` links per cell are common — they can point
    to teams, drivers, articles, or the opponent. When `known_lower` is
    populated we prefer the first link that matches a known bot and skip
    everything else; this filters out team pages like Inertia Labs and
    driver pages like Donald Hutson without hand-curating a blocklist.
    """
    candidates: list[str] = []  # ordered (display name) for fallback
    for a in cell.find_all("a"):
        href = a.get("href") or ""
        if not href.startswith("/wiki/"):
            continue
        slug = href[len("/wiki/") :].split("#", 1)[0]
        if not slug or ":" in slug:  # skip File:, Category:, etc.
            continue
        candidate = slug.replace("_", " ")
        if candidate.lower() == bot_name.lower():
            continue
        display = a.get_text(" ", strip=True) or candidate

        # Prefer known bots when we have a roster — this skips team/driver pages.
        if known_lower:
            canonical = known_lower.get(display.lower()) or known_lower.get(
                candidate.lower()
            )
            if canonical:
                return canonical

        candidates.append(display)

    # No roster constraint, or no anchor matched it.
    if not known_lower and candidates:
        return candidates[0]

    # Last resort: regex on the cell text immediately after "vs".
    match = re.search(
        rf"\b{re.escape(bot_name)}\s+vs\.?\s+([A-Z][\w'!\-]*(?:\s+[A-Z][\w'!\-]*){{0,2}})",
        cell.get_text(" ", strip=True),
    )
    if match:
        candidate = match.group(1).strip()
        if known_lower:
            return known_lower.get(candidate.lower())  # only if recognized
        return candidate
    return None


def _strip_matchup_prefix(text: str, *, bot_name: str, opponent: str) -> str:
    """Remove the leading "Bot A vs Bot B" phrase so heuristics work on the recap."""
    pattern = rf"^{re.escape(bot_name)}\s+vs\.?\s+{re.escape(opponent)}\s*"
    return re.sub(pattern, "", text, count=1, flags=re.IGNORECASE).strip()


def _infer_winner(recap: str, *, bot_name: str, opponent: str) -> str | None:
    """Best-effort winner detection from a free-text fight recap.

    Strategy:
    1. Focus on the recap *tail* (where Fandom recaps almost always
       declare the outcome).
    2. Try every pattern in `_WIN_PATTERNS` (explicit winner mention)
       and `_LOSS_PATTERNS` (explicit loser mention).
    3. If both win- and loss-signals appear for the *same* side, prefer
       the one closer to the end of the recap (later signals usually
       describe the final outcome).
    4. As a last resort, fall back to keyword-density scoring using the
       generic `_WIN_SIGNALS` / `_LOSS_SIGNALS` lexicons.

    Returns the canonical bot name (preserving original casing) of the
    winner, or None when the cues are absent / contradictory.
    """
    if not recap:
        return None

    lower = recap.lower()
    bot_lower = bot_name.lower()
    opp_lower = opponent.lower()
    bot_re = re.escape(bot_lower)
    opp_re = re.escape(opp_lower)

    # Score = char-offset where the strongest signal sits. Later offsets
    # win ties so the *final* outcome dominates earlier narration.
    best_winner: str | None = None
    best_offset: int = -1

    def _consider(winner: str, offset: int) -> None:
        nonlocal best_winner, best_offset
        if offset > best_offset:
            best_winner = winner
            best_offset = offset

    # Explicit "X won" / "X defeated Y" patterns — bot in capture group wins.
    for pattern in _build_win_patterns(bot_re, opp_re):
        for match in re.finditer(pattern, lower):
            token = match.group(1)
            if token == bot_lower:
                _consider(bot_name, match.end())
            elif token == opp_lower:
                _consider(opponent, match.end())

    # Explicit "X was eliminated" patterns — bot in capture group LOSES.
    for pattern in _build_loss_patterns(bot_re, opp_re):
        for match in re.finditer(pattern, lower):
            token = match.group(1)
            if token == bot_lower:
                _consider(opponent, match.end())
            elif token == opp_lower:
                _consider(bot_name, match.end())

    # Subject-less phrasings: "winning the match by KO" is almost always
    # the page-owner winning (Fandom recaps are POV-locked to the page bot).
    # Treat each occurrence as another candidate so it can outrank earlier
    # context-only signals via the offset competition.
    for match in re.finditer(
        r"\bwinning\s+the\s+(?:match|fight|battle)\b", lower
    ):
        _consider(bot_name, match.end())

    if best_winner is not None:
        return best_winner

    # Final fallback: count how many generic win vs loss signals appear
    # in the *tail* of the recap (last ~40% of chars). Tail-bias avoids
    # picking up past-fight context that's common in the first paragraph.
    tail_start = max(0, int(len(lower) * 0.6))
    tail = lower[tail_start:]
    win_hits = sum(1 for kw in _WIN_SIGNALS if kw in tail)
    loss_hits = sum(1 for kw in _LOSS_SIGNALS if kw in tail)
    if win_hits - loss_hits >= 2:
        return bot_name
    if loss_hits - win_hits >= 2:
        return opponent

    return None
