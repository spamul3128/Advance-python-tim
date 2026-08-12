"""
Bright Data Web Scraper API client: trigger, poll, download.
Uses async trigger → poll → download pattern with httpx.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable

import httpx

from src.config.scrapers import BRIGHT_DATA_BASE_URL, LLM_SCRAPERS
from src.models import LLMResult

# Polling: start 5s, max 30s, total timeout 5 min
POLL_INITIAL_SEC = 5
POLL_MAX_SEC = 30
POLL_TIMEOUT_TOTAL_SEC = 300


def _get_auth_headers(api_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }


async def trigger_llm(
    scraper_key: str,
    prompt: str,
    country: str | None,
    *,
    api_token: str,
) -> str:
    """
    Trigger one LLM scraper. Returns snapshot_id.
    Raises on HTTP or parse errors.
    """
    if scraper_key not in LLM_SCRAPERS:
        raise ValueError(f"Unknown scraper key: {scraper_key}")
    cfg = LLM_SCRAPERS[scraper_key]
    dataset_id = cfg["id"]
    url_base = cfg["url"]

    # Request body: per Bright Data docs use {"input":[{"url","prompt","index",...}]}
    # Include country only for scrapers that support it (Gemini returns 400 if extra fields are sent).
    input_item: dict[str, Any] = {
        "url": url_base,
        "prompt": prompt,
        "index": 1,
    }
    if cfg.get("supports_country", True) and country and str(country).strip():
        input_item["country"] = str(country).strip().lower()
    body: dict[str, list[dict[str, Any]]] = {"input": [input_item]}

    url = f"{BRIGHT_DATA_BASE_URL}/trigger"
    params = {"dataset_id": dataset_id, "include_errors": "true"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            url,
            params=params,
            json=body,
            headers=_get_auth_headers(api_token),
        )
        resp.raise_for_status()
        data = resp.json()
    snapshot_id = data.get("snapshot_id")
    if not snapshot_id:
        raise ValueError(f"No snapshot_id in response: {data}")
    return snapshot_id


async def poll_snapshot(
    snapshot_id: str,
    *,
    api_token: str,
) -> dict[str, Any]:
    """
    Poll snapshot until ready. Returns full snapshot payload when status is ready.
    Uses exponential backoff (5s → 30s cap). Timeout after 5 minutes.
    """
    url = f"{BRIGHT_DATA_BASE_URL}/snapshot/{snapshot_id}"
    headers = _get_auth_headers(api_token)
    wait_sec = POLL_INITIAL_SEC
    elapsed = 0.0

    async with httpx.AsyncClient(timeout=60.0) as client:
        while elapsed < POLL_TIMEOUT_TOTAL_SEC:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                raise ValueError(f"Snapshot not found: {snapshot_id}")
            resp.raise_for_status()
            data = resp.json()

            status = data.get("status", "").lower()
            # Ready: either status is ready or we have answer data
            if status == "ready" or "answer_text" in data:
                # If we only got status, fetch full data with format=json
                if "answer_text" not in data:
                    data_resp = await client.get(
                        f"{url}?format=json",
                        headers=headers,
                    )
                    data_resp.raise_for_status()
                    data = data_resp.json()
                return data

            if status in ("failed", "error"):
                raise RuntimeError(f"Snapshot failed: {data.get('error', status)}")

            await asyncio.sleep(wait_sec)
            elapsed += wait_sec
            wait_sec = min(wait_sec * 1.5, POLL_MAX_SEC)

    raise TimeoutError(f"Snapshot {snapshot_id} not ready after {POLL_TIMEOUT_TOTAL_SEC}s")


def _normalize_payload_to_result(
    scraper_key: str,
    prompt: str,
    country: str | None,
    snapshot_id: str,
    raw: dict[str, Any],
    status: str = "success",
    error_message: str | None = None,
) -> LLMResult:
    """Build LLMResult from raw API response. Handles list or single-object response."""
    cfg = LLM_SCRAPERS[scraper_key]
    model_name = cfg["name"]
    timestamp = datetime.now(timezone.utc).isoformat()

    answer_text = ""
    if isinstance(raw.get("data"), list) and len(raw["data"]) > 0:
        first = raw["data"][0]
        answer_text = first.get("answer_text", first.get("answer", "")) or ""
    elif isinstance(raw, list) and len(raw) > 0:
        first = raw[0]
        answer_text = first.get("answer_text", first.get("answer", "")) or ""
    else:
        answer_text = raw.get("answer_text", raw.get("answer", "")) or ""

    return LLMResult(
        model_name=model_name,
        model_key=scraper_key,
        prompt=prompt,
        country=country,
        answer_text=answer_text,
        timestamp=timestamp,
        snapshot_id=snapshot_id,
        status=status,
        error_message=error_message,
        raw_payload=raw,
    )


async def _run_one_llm(
    scraper_key: str,
    prompt: str,
    country: str | None,
    api_token: str,
    progress_callback: Callable[[str, str], None] | None = None,
) -> LLMResult:
    """Trigger, poll, and normalize one LLM. Returns LLMResult (success or error)."""
    def report(phase: str, detail: str = "") -> None:
        if progress_callback:
            progress_callback(phase, detail)

    try:
        report("triggering", "Sending request…")
        snapshot_id = await trigger_llm(scraper_key, prompt, country, api_token=api_token)
        report("polling", "Waiting for response…")
        raw = await poll_snapshot(snapshot_id, api_token=api_token)
        return _normalize_payload_to_result(
            scraper_key, prompt, country, snapshot_id, raw, status="success"
        )
    except TimeoutError as e:
        return _normalize_payload_to_result(
            scraper_key,
            prompt,
            country,
            snapshot_id="",
            raw={},
            status="timeout",
            error_message=str(e),
        )
    except Exception as e:
        return _normalize_payload_to_result(
            scraper_key,
            prompt,
            country,
            snapshot_id="",
            raw={},
            status="error",
            error_message=str(e),
        )


async def run_all_llms(
    prompt: str,
    selected_models: list[str],
    country: str | None,
    *,
    api_token: str,
) -> list[LLMResult]:
    """
    Run the prompt across all selected models in parallel.
    Returns one LLMResult per selected model; failed models have status error/timeout.
    """
    keys_used = [k for k in selected_models if k in LLM_SCRAPERS]
    tasks = [
        _run_one_llm(key, prompt, country, api_token)
        for key in keys_used
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    out: list[LLMResult] = []
    for i, r in enumerate(results):
        key = keys_used[i] if i < len(keys_used) else "unknown"
        if isinstance(r, Exception):
            out.append(
                _normalize_payload_to_result(
                    key,
                    prompt,
                    country,
                    snapshot_id="",
                    raw={},
                    status="error",
                    error_message=str(r),
                )
            )
        else:
            out.append(r)
    return out


def _result_from_exception(
    key: str,
    prompt: str,
    country: str | None,
    exc: Exception,
    status: str = "error",
) -> LLMResult:
    """Build an LLMResult for a failed run."""
    return _normalize_payload_to_result(
        key,
        prompt,
        country,
        snapshot_id="",
        raw={},
        status=status,
        error_message=str(exc),
    )


async def _run_one_and_put(
    key: str,
    prompt: str,
    country: str | None,
    api_token: str,
    progress_cb: Callable[[str, str], None] | None,
    queue: asyncio.Queue,
) -> None:
    """Run one LLM and put (key, result) on the queue when done."""
    try:
        result = await _run_one_llm(
            key, prompt, country, api_token,
            progress_callback=progress_cb,
        )
    except Exception as e:
        result = _result_from_exception(key, prompt, country, e)
    await queue.put((key, result))


async def run_all_llms_with_progress(
    prompt: str,
    selected_models: list[str],
    country: str | None,
    *,
    api_token: str,
    on_model_complete: Callable[[str, LLMResult], None],
    on_phase: Callable[[str, str, str], None] | None = None,
) -> list[LLMResult]:
    """
    Run all selected models in parallel and call on_model_complete(key, result)
    as each model finishes. If on_phase is provided, call on_phase(key, phase, detail)
    for progress steps (e.g. "triggering", "polling"). Returns full list in model order.
    """
    keys_used = [k for k in selected_models if k in LLM_SCRAPERS]

    def progress_for(key: str) -> Callable[[str, str], None] | None:
        if on_phase is None:
            return None
        return lambda phase, detail: on_phase(key, phase, detail)

    queue: asyncio.Queue[tuple[str, LLMResult]] = asyncio.Queue()
    tasks = [
        asyncio.create_task(
            _run_one_and_put(
                key, prompt, country, api_token,
                progress_cb=progress_for(key),
                queue=queue,
            )
        )
        for key in keys_used
    ]

    results_collector: list[LLMResult] = []
    for _ in keys_used:
        key, result = await queue.get()
        results_collector.append(result)
        on_model_complete(key, result)

    await asyncio.gather(*tasks)

    key_order = {k: i for i, k in enumerate(keys_used)}
    return sorted(results_collector, key=lambda r: key_order.get(r.model_key, 999))
