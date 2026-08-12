"""
Orchestrates parallel LLM execution for Streamlit's synchronous context.
"""

import asyncio
from typing import Callable, Optional

from src.api.bright_data import run_all_llms, run_all_llms_with_progress
from src.models import LLMResult


def run_async(coro):
    """
    Run async code in Streamlit's sync context.
    Creates a new event loop and runs the coroutine until complete.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def run_all_llms_sync(
    prompt: str,
    selected_models: list[str],
    country: Optional[str],
    *,
    api_token: str,
) -> list[LLMResult]:
    """
    Synchronous wrapper for run_all_llms. Use from Streamlit.
    """
    return run_async(
        run_all_llms(prompt, selected_models, country, api_token=api_token)
    )


def run_all_llms_with_progress_sync(
    prompt: str,
    selected_models: list[str],
    country: Optional[str],
    *,
    api_token: str,
    on_model_complete: Callable[[str, LLMResult], None],
    on_phase: Optional[Callable[[str, str, str], None]] = None,
) -> list[LLMResult]:
    """
    Same as run_all_llms_sync but calls on_model_complete(key, result) as each
    model finishes. If on_phase(key, phase, detail) is provided, it is called
    for progress steps (e.g. triggering, polling).
    """
    return run_async(
        run_all_llms_with_progress(
            prompt,
            selected_models,
            country,
            api_token=api_token,
            on_model_complete=on_model_complete,
            on_phase=on_phase,
        )
    )
