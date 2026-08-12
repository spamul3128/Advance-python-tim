"""Tests for HTML parsers in `scrapers/parsers/bots_parser.py`.

We use small synthetic HTML fixtures rather than real fetched pages so the
tests are deterministic and remain stable when the real sites change layout.
"""

from __future__ import annotations

from backend.scrapers.parsers.bots_parser import (
    parse_bot_listing_from_official_site,
    parse_bot_profile_from_fandom,
    parse_bot_profile_from_official_site,
)


OFFICIAL_LISTING_HTML = """
<html><body>
  <div class="grid">
    <a href="/bots/tombstone/">
      <h3>Tombstone</h3>
    </a>
    <a href="/bots/huge/">
      <h3>HUGE</h3>
    </a>
    <a href="/about/">About us</a>
  </div>
</body></html>
"""


def test_parse_official_listing_extracts_bots():
    bots = parse_bot_listing_from_official_site(OFFICIAL_LISTING_HTML)
    names = {b["name"] for b in bots}
    assert "Tombstone" in names
    assert "HUGE" in names
    # "/about/" doesn't include "/bots/" so it should be skipped.
    assert all("about" not in b["url"].lower() for b in bots)


OFFICIAL_PROFILE_HTML = """
<html>
<head><title>Tombstone - BattleBots</title></head>
<body>
  <main>
    <h1>Tombstone</h1>
    <img src="https://cdn.example.com/tombstone.jpg" alt="Tombstone bot photo">
    <dl>
      <dt>Weight Class</dt><dd>Heavyweight</dd>
      <dt>Weapon</dt><dd>Spinning bar</dd>
      <dt>Team</dt><dd>Hardcore Robotics</dd>
      <dt>Country</dt><dd>USA</dd>
    </dl>
    <p class="description">Tombstone is an iconic horizontal spinner.</p>
  </main>
</body></html>
"""


def test_parse_official_profile_picks_up_stats():
    data = parse_bot_profile_from_official_site(
        OFFICIAL_PROFILE_HTML, source_url="https://battlebots.com/bots/tombstone/"
    )
    assert data["name"] == "Tombstone"
    assert data["weight_class"] == "Heavyweight"
    assert data["weapon_type"] == "Spinning bar"
    assert data["team_name"] == "Hardcore Robotics"
    assert data["country"] == "USA"
    assert data["image_url"] == "https://cdn.example.com/tombstone.jpg"
    assert data["description"].startswith("Tombstone is")
    assert data["source_url"].endswith("/tombstone/")


FANDOM_PROFILE_HTML = """
<html>
<body>
  <h1 class="page-header__title">Tombstone</h1>
  <aside class="portable-infobox">
    <figure class="pi-image"><a><img src="https://static.wikia.nocookie.net/tombstone.jpg" /></a></figure>
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">Weight Class</h3>
      <div class="pi-data-value">Heavyweight (250 lb)</div>
    </div>
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">Weapon</h3>
      <div class="pi-data-value">Spinning steel bar</div>
    </div>
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">Team</h3>
      <div class="pi-data-value">Hardcore Robotics</div>
    </div>
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">Country</h3>
      <div class="pi-data-value">USA</div>
    </div>
  </aside>
  <div class="mw-parser-output">
    <p>Tombstone is a robot built by Ray Billings that competes in BattleBots.</p>
  </div>
</body></html>
"""


def test_parse_fandom_profile_extracts_infobox_fields():
    data = parse_bot_profile_from_fandom(
        FANDOM_PROFILE_HTML,
        source_url="https://battlebots.fandom.com/wiki/Tombstone",
    )
    assert data["name"] == "Tombstone"
    # Weight is now normalized down to the lbs value (250lbs) from
    # "Heavyweight (250 lb)" to drop the noisy "Heavyweight" prefix.
    assert data["weight_class"] == "250lbs"
    assert data["weapon_type"] == "Spinning steel bar"
    assert data["team_name"] == "Hardcore Robotics"
    assert data["country"] == "USA"
    assert data["image_url"] == "https://static.wikia.nocookie.net/tombstone.jpg"
    assert data["description"].startswith("Tombstone is a robot")


FANDOM_MULTI_WEIGHT_HTML = """
<html>
<body>
  <h1 class="page-header__title">Bite Force</h1>
  <aside class="portable-infobox">
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">Weight</h3>
      <div class="pi-data-value">220lbs (Pro Championship 2009) 250lbs (WC I-Present) 340lbs (NPC Charity Open)</div>
    </div>
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">Weapons</h3>
      <div class="pi-data-value">Grappler (WC I) Vertical bar spinner (WC II-Present)</div>
    </div>
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">From</h3>
      <div class="pi-data-value">Mountain View, CA</div>
    </div>
  </aside>
</body></html>
"""


FANDOM_DUPLICATE_WEAPON_HTML = """
<html>
<body>
  <h1 class="page-header__title">Witch Doctor</h1>
  <aside class="portable-infobox">
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">Weapons</h3>
      <div class="pi-data-value">Vertical disk spinner Vertical drisk spinner</div>
    </div>
  </aside>
</body></html>
"""


def test_parse_fandom_profile_dedupes_repeated_weapon_phrase():
    """Fandom occasionally concatenates the same weapon descriptor twice
    (sometimes with a typo). The normalizer should collapse it back to
    a single clean phrase rather than echoing both copies."""
    data = parse_bot_profile_from_fandom(
        FANDOM_DUPLICATE_WEAPON_HTML,
        source_url="https://battlebots.fandom.com/wiki/Witch_Doctor",
    )
    assert data["weapon_type"] == "Vertical disk spinner"


FANDOM_DUPLICATE_WEAPON_WITH_PRESENT_HTML = """
<html>
<body>
  <h1 class="page-header__title">Witch Doctor</h1>
  <aside class="portable-infobox">
    <div class="pi-item pi-data">
      <h3 class="pi-data-label">Weapons</h3>
      <div class="pi-data-value">Vertical disk spinner Vertical drisk spinner (WC II-Present) Flamethrower</div>
    </div>
  </aside>
</body></html>
"""


def test_parse_fandom_profile_dedupes_when_present_annotation_present():
    """The real Witch Doctor page has the repeated phrase followed by a
    `(WC II-Present)` annotation. The "Present"-matching branch of
    `_primary_weapon` greedily captures the whole repeated prefix, so
    dedup must run on that branch's result too — not just the fallback."""
    data = parse_bot_profile_from_fandom(
        FANDOM_DUPLICATE_WEAPON_WITH_PRESENT_HTML,
        source_url="https://battlebots.fandom.com/wiki/Witch_Doctor",
    )
    assert data["weapon_type"] == "Vertical disk spinner"


def test_parse_fandom_profile_normalizes_multi_entry_values():
    """Multi-historical-entry weights and weapons should collapse to the
    current/primary value, and the 'From' label should map to country."""
    data = parse_bot_profile_from_fandom(
        FANDOM_MULTI_WEIGHT_HTML,
        source_url="https://battlebots.fandom.com/wiki/Bite_Force",
    )
    # 250lbs is the entry annotated "Present" — that wins over the other two.
    assert data["weight_class"] == "250lbs"
    # Vertical bar spinner is the "Present"-annotated weapon.
    assert data["weapon_type"] == "Vertical bar spinner"
    # The raw multi-weapon string is preserved in weapon_description for
    # the LLM to consume if it wants the full history.
    assert "Grappler" in data["weapon_description"]
    # "From" label maps onto country.
    assert data["country"] == "Mountain View, CA"
