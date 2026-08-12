"""
Bright Data SERP API client: fetch Google organic results for a query.
Uses same trigger → poll → download pattern as Web Scraper API.
"""

import asyncio
from typing import Any

import httpx

from src.models import SERPResult

BRIGHT_DATA_BASE_URL = "https://api.brightdata.com/datasets/v3"
SERP_DATASET_ID = "gd_mfz5x93lmsjjjylob"
POLL_INITIAL_SEC = 5
POLL_MAX_SEC = 30
POLL_TIMEOUT_TOTAL_SEC = 300


def _headers(api_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }


async def fetch_serp(
    query: str,
    country: str | None,
    *,
    api_token: str,
    language: str = "en",
    max_results: int = 10,
) -> list[SERPResult]:
    """
    Fetch Google SERP for the given query. Returns top organic results.
    Uses start_page/end_page to limit (1 page ≈ 10 results).
    """
    country_code = (country or "us").upper() if country else "US"
    pages = max(1, (max_results + 9) // 10)
    body = [
        {
            "url": "https://www.google.com/",
            "keyword": query,
            "language": language,
            "country": country_code,
            "start_page": 1,
            "end_page": pages,
        }
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Trigger
        trigger_url = f"{BRIGHT_DATA_BASE_URL}/trigger"
        resp = await client.post(
            trigger_url,
            params={"dataset_id": SERP_DATASET_ID, "include_errors": "true"},
            json=body,
            headers=_headers(api_token),
        )
        resp.raise_for_status()
        data = resp.json()
        snapshot_id = data.get("snapshot_id")
        if not snapshot_id:
            raise ValueError(f"No snapshot_id in SERP response: {data}")

        # Poll until ready
        progress_url = f"{BRIGHT_DATA_BASE_URL}/progress/{snapshot_id}"
        wait_sec = POLL_INITIAL_SEC
        elapsed = 0.0
        while elapsed < POLL_TIMEOUT_TOTAL_SEC:
            prog = await client.get(progress_url, headers=_headers(api_token))
            prog.raise_for_status()
            prog_data = prog.json()
            status = (prog_data.get("status") or "").lower()
            if status == "ready":
                break
            if status in ("failed", "error"):
                raise RuntimeError(f"SERP snapshot failed: {prog_data}")
            await asyncio.sleep(wait_sec)
            elapsed += wait_sec
            wait_sec = min(wait_sec * 1.5, POLL_MAX_SEC)
        else:
            raise TimeoutError(f"SERP snapshot {snapshot_id} not ready after {POLL_TIMEOUT_TOTAL_SEC}s")

        # Download
        download_url = f"{BRIGHT_DATA_BASE_URL}/snapshot/{snapshot_id}?format=json"
        down = await client.get(download_url, headers=_headers(api_token))
        down.raise_for_status()
        results = down.json()

    # Parse organic results: API returns list of records, each may have "organic" array
    out: list[SERPResult] = []
    if isinstance(results, list) and len(results) > 0:
        first = results[0]
        organic = first.get("organic") or first.get("organic_results") or []
    elif isinstance(results, dict):
        organic = results.get("organic") or results.get("organic_results") or []
    else:
        organic = []

    for i, item in enumerate(organic[:max_results]):
        if isinstance(item, dict):
            pos = item.get("position", i + 1)
            title = item.get("title", item.get("link_title", "")) or ""
            url = item.get("url", item.get("link", "")) or ""
            snippet = item.get("snippet", item.get("description", "")) or ""
            out.append(SERPResult(position=pos, title=title, url=url, snippet=snippet))
        else:
            out.append(SERPResult(position=i + 1, title="", url="", snippet=""))

    return out
