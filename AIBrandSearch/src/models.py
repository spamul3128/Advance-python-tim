"""
Data models for LLM results and parsed signals.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LLMResult:
    """Normalized result from a single LLM run via Bright Data."""

    model_name: str
    model_key: str
    prompt: str
    country: Optional[str]
    answer_text: str
    timestamp: str
    snapshot_id: str
    status: str  # "success" | "error" | "timeout"
    error_message: Optional[str] = None
    raw_payload: dict = field(default_factory=dict)


@dataclass
class ParsedSignals:
    """Extracted signals from an LLM response for comparison."""

    model_name: str
    mentioned_tools: list[str]
    mention_positions: dict[str, int]
    answer_shape: str
    word_count: int
    summary: str


@dataclass
class SERPResult:
    """Single organic search result from SERP API."""

    position: int
    title: str
    url: str
    snippet: str
