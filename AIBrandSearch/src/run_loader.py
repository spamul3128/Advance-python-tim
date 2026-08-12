"""
Load a saved run from runs/<timestamp>/ and return in-memory results
for display in the app.
"""

import json
from pathlib import Path
from typing import Any

from src.models import LLMResult, ParsedSignals, SERPResult


def load_run_from_dir(run_dir: Path, prompt_index: int = 0) -> dict[str, Any] | None:
    """
    Load a single run from a runs/<timestamp>/ directory.
    Returns a dict with keys: results (list[LLMResult]), parsed (list[ParsedSignals]),
    prompt (str), country (str|None), serp (list[SERPResult]|None).
    For multi-prompt runs, prompt_index selects which prompt to load (default first).
    Returns None if the run cannot be loaded.
    """
    run_dir = Path(run_dir)
    meta_file = run_dir / "run-metadata.json"
    if not meta_file.exists():
        return None

    try:
        with open(meta_file, encoding="utf-8") as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    models: list[str] = meta.get("models") or []
    if not models:
        return None

    # Keywords used for this run (so comparative analysis uses the same set)
    tracking_keywords: list[str] = meta.get("tracking_keywords") or []

    results: list[LLMResult] = []
    for model_key in models:
        safe_key = model_key.replace(" ", "_")
        results_file = run_dir / f"results-{safe_key}.json"
        if not results_file.exists():
            continue
        try:
            with open(results_file, encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(records, list):
            records = [records]
        idx = min(prompt_index, len(records) - 1)
        if idx < 0:
            continue
        rec = records[idx]
        results.append(
            LLMResult(
                model_name=rec.get("model_name", model_key),
                model_key=rec.get("model_key", model_key),
                prompt=rec.get("prompt", ""),
                country=rec.get("country"),
                answer_text=rec.get("answer_text", ""),
                timestamp=rec.get("timestamp", ""),
                snapshot_id=rec.get("snapshot_id", ""),
                status=rec.get("status", "success"),
                error_message=rec.get("error_message"),
                raw_payload={},
            )
        )

    if not results:
        return None

    prompt = results[0].prompt
    country = results[0].country

    parsed: list[ParsedSignals] = []
    signals_file = run_dir / "parsed-signals.json"
    if signals_file.exists():
        try:
            with open(signals_file, encoding="utf-8") as f:
                signals_list = json.load(f)
        except (json.JSONDecodeError, OSError):
            signals_list = []
        if isinstance(signals_list, list):
            n_models = len(models)
            start = prompt_index * n_models
            for i in range(n_models):
                idx = start + i
                if idx < len(signals_list):
                    s = signals_list[idx]
                    parsed.append(
                        ParsedSignals(
                            model_name=s.get("model_name", ""),
                            mentioned_tools=s.get("mentioned_tools", []),
                            mention_positions=s.get("mention_positions", {}),
                            answer_shape=s.get("answer_shape", "narrative"),
                            word_count=s.get("word_count", 0),
                            summary=s.get("summary", ""),
                        )
                    )

    serp: list[SERPResult] | None = None
    serp_file = run_dir / "serp-results.json"
    if serp_file.exists():
        try:
            with open(serp_file, encoding="utf-8") as f:
                serp_list = json.load(f)
        except (json.JSONDecodeError, OSError):
            serp_list = []
        if isinstance(serp_list, list):
            serp = []
            for s in serp_list:
                if isinstance(s, dict):
                    serp.append(
                        SERPResult(
                            position=s.get("position", 0),
                            title=s.get("title", ""),
                            url=s.get("url", ""),
                            snippet=s.get("snippet", ""),
                        )
                    )
        if serp is not None and len(serp) == 0:
            serp = None

    analysis_text: str | None = None
    analysis_file = run_dir / "analysis.md"
    if analysis_file.exists():
        try:
            analysis_text = analysis_file.read_text(encoding="utf-8")
        except OSError:
            pass

    prompts_list: list[str] = meta.get("prompts") or []
    return {
        "results": results,
        "parsed": parsed if parsed else _fallback_parsed(results, tracking_keywords),
        "prompt": prompt,
        "country": country,
        "serp": serp,
        "analysis_text": analysis_text,
        "tracking_keywords": tracking_keywords,
        "prompts_list": prompts_list,
    }


def _fallback_parsed(
    results: list[LLMResult],
    tracking_keywords: list[str] | None = None,
) -> list[ParsedSignals]:
    """Build ParsedSignals when parsed-signals.json is missing, using the run's stored keywords."""
    from src.config import DEFAULT_TRACKING_KEYWORDS
    from src.parser.parser import parse_result
    keywords = tracking_keywords if tracking_keywords else DEFAULT_TRACKING_KEYWORDS
    return [parse_result(r, keywords) for r in results]
