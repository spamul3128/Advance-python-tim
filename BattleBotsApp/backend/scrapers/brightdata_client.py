"""Thin wrapper around the Bright Data Web Unlocker API.

Bright Data exposes an HTTP endpoint that fetches a target URL through their
anti-bot infrastructure and returns the rendered HTML. Docs:
    https://docs.brightdata.com/scraping-automation/web-unlocker/quickstart

Endpoint:
    POST https://api.brightdata.com/request
    Authorization: Bearer <API_TOKEN>
    Body (JSON):
        {
          "zone":    "<web_unlocker_zone_name>",
          "url":     "<target_url>",
          "format":  "raw",
          "country": "us",
          "method":  "GET"
        }

`format=raw` makes the API return the raw response body (HTML) as the response
body of our request — which is what we want for HTML parsing.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from ..config import settings

logger = logging.getLogger(__name__)

BRIGHT_DATA_ENDPOINT = "https://api.brightdata.com/request"


class BrightDataError(RuntimeError):
    """Raised when the Bright Data API returns an error."""


class BrightDataClient:
    """Synchronous client for the Bright Data Web Unlocker API.

    Designed for the scraper scripts. For request-time scraping inside the
    FastAPI app, swap to httpx.AsyncClient — the JSON contract is identical.
    """

    def __init__(
        self,
        api_token: str | None = None,
        zone: str | None = None,
        country: str | None = None,
        timeout_seconds: int | None = None,
        request_delay_seconds: float | None = None,
        max_retries: int = 3,
    ) -> None:
        self.api_token = api_token or settings.brightdata_api_token
        self.zone = zone or settings.brightdata_web_unlocker_zone
        self.country = country or settings.brightdata_country
        self.timeout_seconds = (
            timeout_seconds or settings.brightdata_timeout_seconds
        )
        self.request_delay_seconds = (
            request_delay_seconds
            if request_delay_seconds is not None
            else settings.scraper_request_delay_seconds
        )
        self.max_retries = max_retries

        if not self.api_token:
            raise BrightDataError(
                "BRIGHTDATA_API_TOKEN is not configured. See backend/.env.example."
            )
        if not self.zone:
            raise BrightDataError(
                "BRIGHTDATA_WEB_UNLOCKER_ZONE is not configured."
            )

        self._client = httpx.Client(
            timeout=self.timeout_seconds,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "Accept": "*/*",
            },
        )

    # -- Resource management -------------------------------------------------
    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BrightDataClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # -- Public API ----------------------------------------------------------
    def fetch_html(self, url: str, *, extra: dict[str, Any] | None = None) -> str:
        """Fetch a URL through Bright Data and return the raw HTML body.

        Retries on transient HTTP errors with exponential backoff.
        """
        payload: dict[str, Any] = {
            "zone": self.zone,
            "url": url,
            "format": "raw",
            "method": "GET",
        }
        if self.country:
            payload["country"] = self.country
        if extra:
            payload.update(extra)

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                self._respect_rate_limit()
                logger.debug("Bright Data fetch (attempt %d): %s", attempt, url)
                response = self._client.post(BRIGHT_DATA_ENDPOINT, json=payload)
                if response.status_code == 200:
                    return response.text
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise httpx.HTTPStatusError(
                        f"Transient {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                # Non-retryable: surface the body so the user sees what's wrong.
                raise BrightDataError(
                    f"Bright Data returned HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )
            except (httpx.HTTPError, httpx.HTTPStatusError) as err:
                last_error = err
                backoff = min(2 ** (attempt - 1), 30)
                logger.warning(
                    "Bright Data request failed (attempt %d/%d) for %s: %s. "
                    "Retrying in %ds.",
                    attempt,
                    self.max_retries,
                    url,
                    err,
                    backoff,
                )
                time.sleep(backoff)

        raise BrightDataError(
            f"Bright Data request failed after {self.max_retries} attempts "
            f"for {url}: {last_error}"
        ) from last_error

    # -- Internals -----------------------------------------------------------
    _last_request_time: float = 0.0

    def _respect_rate_limit(self) -> None:
        """Sleep so successive requests are spaced at least `delay` apart."""
        if self.request_delay_seconds <= 0:
            return
        elapsed = time.monotonic() - self._last_request_time
        wait = self.request_delay_seconds - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_time = time.monotonic()
