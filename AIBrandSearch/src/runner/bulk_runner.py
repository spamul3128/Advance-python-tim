"""
Runs multiple prompts across selected LLMs and saves results to ./runs.
Uses project root for runs dir so saves are consistent regardless of cwd.
Runs all prompts in parallel (each prompt runs all its models in parallel).
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from src.api.bright_data import run_all_llms
from src.models import LLMResult, ParsedSignals, SERPResult
from src.parser.parser import parse_result
from src.runner.prompt_runner import run_async

# Project root: src/runner/bulk_runner.py -> parent.parent = src, parent.parent.parent = root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RUNS_DIR = _PROJECT_ROOT / "runs"
DEFAULT_KEYWORDS = [
    "Bright Data", "SEMrush", "Ahrefs", "Moz", "Surfer",
    "Otterly", "Peec", "Scrunch", "BrandWatch", "HubSpot",
]


def _run_dir_name() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")


def _ensure_runs_dir() -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return RUNS_DIR


def _result_to_record(r: LLMResult) -> dict[str, Any]:
    """Serialize one LLMResult for JSON storage."""
    return {
        "model_name": r.model_name,
        "model_key": r.model_key,
        "prompt": r.prompt,
        "country": r.country,
        "answer_text": r.answer_text,
        "timestamp": r.timestamp,
        "snapshot_id": r.snapshot_id,
        "status": r.status,
        "error_message": r.error_message,
    }


async def _run_bulk_parallel(
    valid_prompts: list[tuple[int, dict[str, Any]]],
    selected_models: list[str],
    default_country: Optional[str],
    api_token: str,
    on_progress: Optional[Callable[[int, int, str], None]],
) -> tuple[list[LLMResult], list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """
    Run every (prompt × models) in parallel. Each prompt runs all its models in parallel;
    all prompts run concurrently. Returns (all_llm_results, prompts_meta, by_model).
    """
    total = len(valid_prompts)
    completed_count: list[int] = [0]  # mutable so tasks can update

    async def run_one_prompt(idx: int, item: dict[str, Any]) -> tuple[int, str, Optional[str], list[LLMResult]]:
        prompt_text = (item.get("prompt") or "").strip()
        country = item.get("country") or default_country
        try:
            results = await run_all_llms(
                prompt_text,
                selected_models,
                country,
                api_token=api_token,
            )
        except Exception as e:
            results = [
                LLMResult(
                    model_name=m,
                    model_key=m,
                    prompt=prompt_text,
                    country=country,
                    answer_text="",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    snapshot_id="",
                    status="error",
                    error_message=str(e),
                    raw_payload={},
                )
                for m in selected_models
            ]
        completed_count[0] += 1
        if on_progress:
            on_progress(completed_count[0], total, prompt_text)
        return (idx, prompt_text, country, results)

    tasks = [run_one_prompt(idx, item) for idx, item in valid_prompts]
    gathered = await asyncio.gather(*tasks, return_exceptions=True)

    all_llm_results: list[LLMResult] = []
    prompts_meta: list[dict[str, Any]] = []
    by_model: dict[str, list[dict[str, Any]]] = {m: [] for m in selected_models}

    for (idx, item), raw in zip(valid_prompts, gathered):
        prompt_text = (item.get("prompt") or "").strip()
        country = item.get("country") or default_country
        if isinstance(raw, Exception):
            for m in selected_models:
                err_result = LLMResult(
                    model_name=m,
                    model_key=m,
                    prompt=prompt_text,
                    country=country,
                    answer_text="",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    snapshot_id="",
                    status="error",
                    error_message=str(raw),
                    raw_payload={},
                )
                all_llm_results.append(err_result)
                by_model.setdefault(m, []).append(_result_to_record(err_result))
            prompts_meta.append({"index": idx, "prompt": prompt_text, "country": country, "result_count": len(selected_models)})
            continue
        _, _prompt_text, _country, results = raw
        all_llm_results.extend(results)
        prompts_meta.append({"index": idx, "prompt": prompt_text, "country": country, "result_count": len(results)})
        for r in results:
            by_model.setdefault(r.model_key, []).append(_result_to_record(r))

    return all_llm_results, prompts_meta, by_model


def run_bulk(
    prompts: list[dict[str, Any]],
    selected_models: list[str],
    default_country: Optional[str],
    api_token: str,
    tracking_keywords: Optional[list[str]] = None,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Run each prompt in prompts across selected_models. Each prompt dict can have
    "prompt" and optional "country". Save all results under runs/<timestamp>/.
    Optional on_progress(current_1based, total, prompt_text) is called before each prompt.
    Returns (run_dir_name, list of per-prompt result summaries for UI).
    """
    keywords = tracking_keywords or DEFAULT_KEYWORDS
    run_id = _run_dir_name()
    base = _ensure_runs_dir() / run_id
    base.mkdir(parents=True, exist_ok=True)

    valid_prompts = [(i, p) for i, p in enumerate(prompts) if (p.get("prompt") or "").strip()]
    total_prompts = len(valid_prompts)

    all_llm_results, prompts_meta, by_model = run_async(
        _run_bulk_parallel(
            valid_prompts,
            selected_models,
            default_country,
            api_token,
            on_progress=on_progress,
        )
    )

    for model_key, recs in by_model.items():
        safe_key = model_key.replace(" ", "_")
        with open(base / f"results-{safe_key}.json", "w", encoding="utf-8") as f:
            json.dump(recs, f, indent=2)

    # Parsed signals for all results
    parsed = [
        parse_result(r, keywords)
        for r in all_llm_results
    ]
    signals_data = [
        {
            "model_name": p.model_name,
            "mentioned_tools": p.mentioned_tools,
            "mention_positions": p.mention_positions,
            "answer_shape": p.answer_shape,
            "word_count": p.word_count,
            "summary": p.summary,
        }
        for p in parsed
    ]
    with open(base / "parsed-signals.json", "w", encoding="utf-8") as f:
        json.dump(signals_data, f, indent=2)

    # Run metadata (include tracking_keywords so comparative analysis uses the same keywords)
    # Preserve per-prompt countries when present (e.g. from batch generation with MY, ID, CN).
    prompts_with_country = [
        {"prompt": p.get("prompt", ""), "country": p.get("country") or default_country}
        for p in prompts
        if p.get("prompt")
    ]
    prompts_list = [p["prompt"] for p in prompts_with_country]
    meta = {
        "timestamp": run_id,
        "prompts": prompts_list,
        "models": selected_models,
        "country": default_country,
        "prompt_count": len(prompts_meta),
        "tracking_keywords": keywords,
    }
    with open(base / "run-metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Dedicated prompts file: keep each prompt's actual country for replay/audit
    with open(base / "prompts.json", "w", encoding="utf-8") as f:
        json.dump(prompts_with_country, f, indent=2)

    return run_id, prompts_meta


def save_single_run(
    results: list[LLMResult],
    parsed: list[ParsedSignals],
    prompt: str,
    country: Optional[str],
    serp: Optional[list[SERPResult]] = None,
    tracking_keywords: Optional[list[str]] = None,
) -> str:
    """
    Save a single run (e.g. from the main UI) to runs/<timestamp>/.
    Same format as bulk runs so it appears in Past runs. Returns run_id.
    Stores tracking_keywords so comparative analysis uses the same keywords when loading.
    """
    run_id = _run_dir_name()
    base = _ensure_runs_dir() / run_id
    base.mkdir(parents=True, exist_ok=True)

    models = [r.model_key for r in results]
    keywords = tracking_keywords or DEFAULT_KEYWORDS
    meta = {
        "timestamp": run_id,
        "prompts": [prompt],
        "models": models,
        "country": country,
        "prompt_count": 1,
        "tracking_keywords": keywords,
    }
    with open(base / "run-metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Dedicated prompts file
    with open(base / "prompts.json", "w", encoding="utf-8") as f:
        json.dump([{"prompt": prompt, "country": country}], f, indent=2)

    for r in results:
        rec = {
            "model_name": r.model_name,
            "model_key": r.model_key,
            "prompt": r.prompt,
            "country": r.country,
            "answer_text": r.answer_text,
            "timestamp": r.timestamp,
            "snapshot_id": r.snapshot_id,
            "status": r.status,
            "error_message": r.error_message,
        }
        safe_key = r.model_key.replace(" ", "_")
        with open(base / f"results-{safe_key}.json", "w", encoding="utf-8") as f:
            json.dump([rec], f, indent=2)

    signals_data = [
        {
            "model_name": p.model_name,
            "mentioned_tools": p.mentioned_tools,
            "mention_positions": p.mention_positions,
            "answer_shape": p.answer_shape,
            "word_count": p.word_count,
            "summary": p.summary,
        }
        for p in parsed
    ]
    with open(base / "parsed-signals.json", "w", encoding="utf-8") as f:
        json.dump(signals_data, f, indent=2)

    if serp:
        serp_data = [
            {"position": s.position, "title": s.title, "url": s.url, "snippet": s.snippet}
            for s in serp
        ]
        with open(base / "serp-results.json", "w", encoding="utf-8") as f:
            json.dump(serp_data, f, indent=2)

    return run_id


def get_run_dir(run_id: str) -> Path:
    """Return the path to a run directory. Does not create it."""
    return RUNS_DIR / run_id


def save_serp_to_run(run_id: str, serp: list[SERPResult]) -> bool:
    """Append SERP results to an existing run. Returns True if saved."""
    base = get_run_dir(run_id)
    if not base.exists() or not base.is_dir():
        return False
    serp_data = [
        {"position": s.position, "title": s.title, "url": s.url, "snippet": s.snippet}
        for s in serp
    ]
    try:
        with open(base / "serp-results.json", "w", encoding="utf-8") as f:
            json.dump(serp_data, f, indent=2)
        return True
    except OSError:
        return False


def save_analysis_to_run(run_id: str, analysis_text: str) -> bool:
    """Save comparative analysis text to an existing run. Returns True if saved."""
    base = get_run_dir(run_id)
    if not base.exists() or not base.is_dir():
        return False
    try:
        with open(base / "analysis.md", "w", encoding="utf-8") as f:
            f.write(analysis_text)
        return True
    except OSError:
        return False
