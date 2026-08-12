"""Parsers for BattleBots bot profile pages.

Two sources are supported:

1. battlebots.com  — the official site. The exact HTML structure changes
   often, so we use defensive selectors and fall back gracefully.

2. battlebots.fandom.com — the Fandom wiki. Infoboxes have a stable layout
   that yields clean structured data.

Both functions return a plain dict matching the columns of the `bots`
table (with `name` being the only required field). Optional fields default
to None when the source doesn't provide them.
"""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# battlebots.com — the official site
# ---------------------------------------------------------------------------
def parse_bot_listing_from_official_site(
    html: str, base_url: str = "https://battlebots.com"
) -> list[dict[str, str]]:
    """Extract bot name + profile URL pairs from the /the-bots/ listing page.

    The page is a Webflow-rendered grid; each bot card is wrapped in an
    anchor whose href points to the profile. Selectors are deliberately
    permissive — we hunt for anchors that look like bot links.
    """
    soup = BeautifulSoup(html, "lxml")
    seen: set[str] = set()
    results: list[dict[str, str]] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "/bots/" not in href and "/the-bots/" not in href:
            continue

        # Find the card's title — try common patterns in order.
        name = _find_card_title(anchor)
        if not name:
            continue

        full_url = urljoin(base_url, href)
        key = name.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        results.append({"name": name.strip(), "url": full_url})

    return results


def _find_card_title(anchor: Tag) -> str | None:
    """Best-effort search for the bot name inside a card anchor."""
    for selector in ("h1", "h2", "h3", "h4", "[class*='name']", "[class*='title']"):
        node = anchor.select_one(selector)
        if node and node.get_text(strip=True):
            return node.get_text(strip=True)
    text = anchor.get_text(" ", strip=True)
    return text if text else None


def parse_bot_profile_from_official_site(
    html: str, source_url: str
) -> dict[str, Any]:
    """Extract structured fields from a single bot's profile page.

    Fields that can't be located are returned as None. The 'name' field
    falls back to the page's <title> if no headline is found.
    """
    soup = BeautifulSoup(html, "lxml")

    name = _text_or_none(soup.select_one("h1"))
    if not name and soup.title:
        name = re.sub(r"\s*[-|]\s*BattleBots.*$", "", soup.title.get_text()).strip()

    image = soup.select_one(
        "img[src*='bot'], img[alt*='bot'], picture img, main img"
    )
    image_url = image["src"] if image and image.has_attr("src") else None

    # Many profile templates use definition lists or label/value pairs for
    # stats. We sweep up everything that looks like one.
    stats = _collect_label_value_pairs(soup)

    description = _text_or_none(
        soup.select_one("[class*='description'], [class*='bio'], main p")
    )

    return {
        "name": name,
        "weight_class": stats.get("weight_class"),
        "weapon_type": stats.get("weapon"),
        "weapon_description": stats.get("weapon_description"),
        "team_name": stats.get("team"),
        "country": stats.get("country") or stats.get("location"),
        "image_url": image_url,
        "description": description,
        "source_url": source_url,
    }


# ---------------------------------------------------------------------------
# battlebots.fandom.com — the Fandom wiki
# ---------------------------------------------------------------------------
def parse_bot_profile_from_fandom(
    html: str, source_url: str
) -> dict[str, Any]:
    """Extract structured fields from a Fandom wiki bot article.

    Fandom infoboxes use a stable `aside.portable-infobox` layout with
    `<div class="pi-item pi-data">` rows holding label/value pairs. The
    raw values often concatenate multiple historical entries (e.g.
    "220lbs (Pro Championship 2009) 250lbs (WC I-Present)" for weight),
    so we normalize them to the primary/current value where possible.
    """
    soup = BeautifulSoup(html, "lxml")

    name = _text_or_none(soup.select_one("h1.page-header__title, h1#firstHeading"))
    infobox = soup.select_one("aside.portable-infobox")
    fields: dict[str, str] = {}

    if infobox is not None:
        for row in infobox.select("div.pi-item.pi-data"):
            label_node = row.select_one(".pi-data-label")
            value_node = row.select_one(".pi-data-value")
            if label_node and value_node:
                label = label_node.get_text(strip=True).lower()
                value = value_node.get_text(" ", strip=True)
                fields[_normalize_label(label)] = value

    image_node = (
        infobox.select_one("img") if infobox else soup.select_one("figure.thumb img")
    )
    image_url = (
        image_node.get("src") or image_node.get("data-src")
        if image_node
        else None
    )

    description = None
    for para in soup.select(".mw-parser-output > p"):
        text = para.get_text(" ", strip=True)
        if text and len(text) > 40:
            description = text
            break

    raw_weight = fields.get("weight_class") or fields.get("weight")
    raw_weapon = fields.get("weapon") or fields.get("weapons")
    raw_country = (
        fields.get("country")
        or fields.get("hometown")
        or fields.get("origin")
        or fields.get("from")  # Fandom infoboxes commonly use "From"
    )

    return {
        "name": name,
        "weight_class": _primary_weight(raw_weight),
        "weapon_type": _primary_weapon(raw_weapon),
        "weapon_description": fields.get("weapon_description") or raw_weapon,
        "team_name": fields.get("team"),
        "country": _normalize_country(raw_country),
        "image_url": image_url,
        "description": description,
        "source_url": source_url,
    }


def _primary_weight(raw: str | None) -> str | None:
    """Pick the primary/current weight from a noisy multi-entry value.

    Examples:
        "220lbs (Pro Championship 2009) 250lbs (WC I-Present) 340lbs ..."
        → "250lbs"
        "250lbs"
        → "250lbs"
        "250lbs (WC V-Present) 247lbs (WC IV)"
        → "250lbs" (the entry annotated as "Present" wins)
    """
    if not raw:
        return None

    # Find all `<number> lbs` weight tokens with their optional
    # annotation in parentheses. Prefer the one whose annotation
    # contains "present" (current weight); else fall back to the first.
    pattern = re.compile(
        r"(\d{2,4})\s*(?:lbs?|kg)\s*(?:\(([^)]*)\))?",
        flags=re.IGNORECASE,
    )
    matches = list(pattern.finditer(raw))
    if not matches:
        cleaned = raw.strip()
        return cleaned or None

    for m in matches:
        annotation = (m.group(2) or "").lower()
        if "present" in annotation:
            return f"{m.group(1)}lbs"

    return f"{matches[0].group(1)}lbs"


def _primary_weapon(raw: str | None) -> str | None:
    """Pick the primary weapon descriptor from a multi-entry value.

    Fandom often concatenates every weapon variant a bot has ever used,
    e.g. "Grabbing jaws (WC I-WC III) Flamethrower (WC I-WC III) Spring
    flipper (WC II) Vertical bar spinner (WC II) ...". We extract the
    first descriptor that's not parenthetical noise.
    """
    if not raw:
        return None

    cleaned = re.sub(r"\[\s*\d+\s*\]", "", raw)  # strip [1] footnotes
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return None

    # Try to find a "Present"-annotated weapon first.
    present_match = re.search(
        r"([A-Za-z][A-Za-z\s\-]+?)\s*\([^)]*present[^)]*\)",
        cleaned,
        flags=re.IGNORECASE,
    )
    if present_match:
        candidate = present_match.group(1).strip()
    else:
        # Fall back to the leading clause before the first parenthetical.
        head = re.split(r"\s*\(", cleaned, maxsplit=1)[0].strip()
        candidate = head if head else cleaned

    # Fandom infoboxes sometimes concatenate the same weapon twice (e.g.
    # "Vertical disk spinner Vertical disk spinner" or with a typo,
    # "Vertical disk spinner Vertical drisk spinner"). Collapse those
    # into a single descriptor so the UI shows the clean name. We do
    # this for BOTH the "Present"-annotated and fallback branches because
    # the non-greedy regex above can still capture a repeated prefix.
    candidate = _dedupe_repeated_phrase(candidate)
    return candidate[:80]


def _dedupe_repeated_phrase(text: str) -> str:
    """Collapse an immediate phrase repetition such as
    "Vertical disk spinner Vertical disk spinner" → "Vertical disk spinner".
    """
    words = text.split()
    half = len(words) // 2
    for size in range(half, 1, -1):
        head = " ".join(words[:size])
        tail = " ".join(words[size : size * 2])
        # Exact repetition.
        if head == tail:
            return " ".join(words[:size] + words[size * 2 :]).strip()
        # Allow a single-char typo per word (e.g. "disk" vs "drisk").
        if _phrases_near_equal(head, tail):
            return " ".join(words[:size] + words[size * 2 :]).strip()
    return text


def _phrases_near_equal(a: str, b: str, *, max_per_word: int = 1) -> bool:
    """True when each word in `a` is within `max_per_word` edits of the
    corresponding word in `b`. Uses true Levenshtein distance so single
    insertions/deletions/substitutions count as one edit — enough to
    catch the "disk" vs "drisk" Witch Doctor typo without pulling in
    an external dependency.
    """
    aw, bw = a.split(), b.split()
    if len(aw) != len(bw):
        return False
    return all(_edit_distance(x, y) <= max_per_word for x, y in zip(aw, bw))


def _edit_distance(a: str, b: str) -> int:
    """Classic dynamic-programming Levenshtein distance.

    Returns the minimum number of single-character insertions,
    deletions, or substitutions required to turn `a` into `b`.
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cur[j] = min(
                cur[j - 1] + 1,         # insertion
                prev[j] + 1,            # deletion
                prev[j - 1] + (0 if ca == cb else 1),  # substitution
            )
        prev = cur
    return prev[-1]


def _normalize_country(raw: str | None) -> str | None:
    """Trim Fandom location strings down to a useful country/region label.

    Inputs we see:
        "Placerville, CA"     → "Placerville, CA"
        "Long Beach, CA, USA" → "Long Beach, CA, USA"
        "Boston, Massachusetts" → "Boston, Massachusetts"

    We just strip whitespace / footnote markers and return as-is —
    presenting the full hometown is more useful than guessing country.
    """
    if not raw:
        return None
    cleaned = re.sub(r"\[\s*\d+\s*\]", "", raw).strip()
    return cleaned or None


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
_LABEL_ALIASES = {
    "weight class": "weight_class",
    "weight": "weight_class",
    "weapons": "weapon",
    "weapon(s)": "weapon",
    "primary weapon": "weapon",
    "country": "country",
    "hometown": "country",
    "origin": "country",
    "from": "country",  # Fandom uses this label for hometown.
    "based in": "country",
    "team": "team",
    "team name": "team",
    "team members": "team_members",
}


def _normalize_label(label: str) -> str:
    """Map a free-form label like 'Weight Class:' to a canonical key."""
    cleaned = re.sub(r"[:\u00a0]+$", "", label.strip()).lower()
    return _LABEL_ALIASES.get(cleaned, cleaned.replace(" ", "_"))


def _collect_label_value_pairs(soup: BeautifulSoup) -> dict[str, str]:
    """Best-effort harvest of stat-like label/value pairs from a profile page."""
    result: dict[str, str] = {}

    # <dl><dt>Weight Class</dt><dd>Heavyweight</dd></dl>
    for dl in soup.find_all("dl"):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            key = _normalize_label(dt.get_text(strip=True))
            result[key] = dd.get_text(" ", strip=True)

    # Generic "Label: Value" inline patterns we sometimes see.
    for el in soup.find_all(["p", "li", "span", "div"]):
        text = el.get_text(" ", strip=True)
        match = re.match(r"^([A-Za-z][A-Za-z ]{2,30}):\s*(.+)$", text)
        if not match:
            continue
        key = _normalize_label(match.group(1))
        value = match.group(2).strip()
        if key and value and key not in result:
            result[key] = value

    return result


def _text_or_none(node: Tag | None) -> str | None:
    if node is None:
        return None
    text = node.get_text(" ", strip=True)
    return text or None
