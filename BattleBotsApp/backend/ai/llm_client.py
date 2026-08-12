"""Provider-agnostic LLM client for the scouting-report use case.

Supports OpenAI and Anthropic, selected via the LLM_PROVIDER env var. Both
backends are called synchronously — predictions are a one-shot operation, so
async buys us nothing here.

We force JSON output where the API supports it and fall back to robust
extraction (strip code fences, pluck the first {...} block) so the predictor
always gets a parseable response.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from ..config import settings

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Raised when the LLM call fails or returns un-parseable content."""


@dataclass(frozen=True)
class FactCitation:
    """A single grounded claim tied to a catalog fact ID."""

    fact_id: str
    claim: str
    supports: str = "neutral"


@dataclass(frozen=True)
class ScoutingReport:
    """Structured prediction payload returned to the API layer.

    `reasoning_steps` + `evidence_citations` make the model's work auditable —
    they surface the chain of thought (in moderation, not verbatim) and the
    specific data points it leaned on. Both are optional on the wire so older
    cached predictions that predate the schema still hydrate cleanly.
    """

    winner: str
    confidence: float
    method_prediction: str
    key_factors: list[str]
    weapon_matchup: str
    narrative: str
    x_factor: str
    raw_response: str
    model: str
    reasoning_steps: list[str]
    evidence_citations: list[str]
    fact_citations: list[FactCitation]


class LLMClient:
    """Thin wrapper that picks OpenAI or Anthropic based on env config."""

    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or settings.llm_provider).lower()
        if self.provider not in {"openai", "anthropic"}:
            raise LLMError(f"Unsupported LLM_PROVIDER: {self.provider!r}")

        if self.provider == "openai":
            if not settings.openai_api_key:
                raise LLMError("OPENAI_API_KEY is not set in backend/.env.")
            # Lazy import so users without openai installed still get a clean error.
            from openai import OpenAI

            self._openai = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        else:
            if not settings.anthropic_api_key:
                raise LLMError("ANTHROPIC_API_KEY is not set in backend/.env.")
            from anthropic import Anthropic

            self._anthropic = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model

    # -- Public API ---------------------------------------------------------
    def generate_scouting_report(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        bot_a_name: str,
        bot_b_name: str,
        refine_confidence: Any | None = None,
    ) -> ScoutingReport:
        """Call the LLM, parse JSON, and return a typed scouting report."""
        raw = self._call(system_prompt=system_prompt, user_prompt=user_prompt)
        payload = self._extract_json(raw)
        report = self._coerce_report(payload, raw, bot_a_name, bot_b_name)
        if refine_confidence is not None:
            adjusted = refine_confidence(report.confidence, report.winner)
            return ScoutingReport(
                winner=report.winner,
                confidence=adjusted,
                method_prediction=report.method_prediction,
                key_factors=report.key_factors,
                weapon_matchup=report.weapon_matchup,
                narrative=report.narrative,
                x_factor=report.x_factor,
                raw_response=report.raw_response,
                model=report.model,
                reasoning_steps=report.reasoning_steps,
                evidence_citations=report.evidence_citations,
                fact_citations=report.fact_citations,
            )
        return report

    # -- Provider dispatch --------------------------------------------------
    def _call(self, *, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)
        return self._call_anthropic(system_prompt, user_prompt)

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        base_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.45,
        }
        try:
            response = self._openai_chat_create(base_kwargs, max_output_tokens=2800)
        except Exception as err:
            raise _wrap_provider_error("OpenAI", err) from err
        return response.choices[0].message.content or ""

    def _openai_chat_create(self, base_kwargs: dict[str, Any], *, max_output_tokens: int):
        """Create a chat completion, picking the token limit param the model accepts."""
        from openai import BadRequestError

        last_err: Exception | None = None
        for token_param in ("max_completion_tokens", "max_tokens"):
            try:
                return self._openai.chat.completions.create(
                    **base_kwargs,
                    **{token_param: max_output_tokens},
                )
            except BadRequestError as err:
                last_err = err
                message = str(err).lower()
                if token_param in message or "unsupported parameter" in message:
                    continue
                raise
        if last_err is not None:
            raise last_err
        raise LLMError("OpenAI chat completion failed with no token limit parameter.")

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self._anthropic.messages.create(
                model=self.model,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                max_tokens=2800,
                temperature=0.45,
            )
        except Exception as err:
            raise _wrap_provider_error("Anthropic", err) from err
        parts = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "".join(parts)

    # -- Response parsing ---------------------------------------------------
    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        """Pull the first JSON object out of the response.

        Handles bare JSON, markdown-fenced JSON, and stray prose before/after.
        """
        if not raw.strip():
            raise LLMError("LLM returned an empty response.")

        # Try direct parse first (covers the json_object response format).
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Strip code fences if present.
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if fence_match:
            try:
                return json.loads(fence_match.group(1))
            except json.JSONDecodeError:
                pass

        # Last resort: grab everything between the first { and last }.
        brace_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError as err:
                raise LLMError(f"LLM response was not valid JSON: {err}") from err

        raise LLMError(f"Could not locate JSON in LLM response: {raw[:200]}…")

    def _coerce_report(
        self,
        payload: dict[str, Any],
        raw: str,
        bot_a_name: str,
        bot_b_name: str,
    ) -> ScoutingReport:
        winner = str(payload.get("winner") or "").strip()
        # Be forgiving about case / extra whitespace.
        normalized = {bot_a_name.lower(): bot_a_name, bot_b_name.lower(): bot_b_name}
        winner = normalized.get(winner.lower(), winner)

        confidence = round(_clamp_float(payload.get("confidence"), default=0.5), 3)
        method = str(payload.get("method_prediction") or "UNCLEAR").strip().upper()
        if method not in {"KO", "TKO", "JD", "UNCLEAR"}:
            method = "UNCLEAR"

        key_factors = _coerce_string_list(payload.get("key_factors"))
        reasoning_steps = _coerce_string_list(payload.get("reasoning_steps"))
        evidence_citations = _coerce_string_list(payload.get("evidence_citations"))
        fact_citations = _coerce_fact_citations(payload.get("fact_citations"))

        return ScoutingReport(
            winner=winner or bot_a_name,
            confidence=confidence,
            method_prediction=method,
            key_factors=key_factors,
            weapon_matchup=str(payload.get("weapon_matchup") or "").strip(),
            narrative=str(payload.get("narrative") or "").strip(),
            x_factor=str(payload.get("x_factor") or "").strip(),
            raw_response=raw,
            model=self.model,
            reasoning_steps=reasoning_steps,
            evidence_citations=evidence_citations,
            fact_citations=fact_citations,
        )


def _clamp_float(value: Any, *, default: float) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    if f != f:  # NaN check
        return default
    return max(0.0, min(1.0, f))


def _coerce_fact_citations(value: Any) -> list[FactCitation]:
    if not value:
        return []
    if not isinstance(value, list):
        value = [value]
    out: list[FactCitation] = []
    for item in value:
        if isinstance(item, dict):
            fact_id = str(item.get("fact_id") or item.get("id") or "").strip()
            claim = str(item.get("claim") or "").strip()
            supports = str(item.get("supports") or "neutral").strip().lower()
            if fact_id and claim:
                if supports not in {"winner", "loser", "neutral"}:
                    supports = "neutral"
                out.append(FactCitation(fact_id=fact_id, claim=claim, supports=supports))
        elif isinstance(item, str) and item.strip():
            out.append(FactCitation(fact_id="", claim=item.strip(), supports="neutral"))
    return out


def _wrap_provider_error(provider: str, err: Exception) -> LLMError:
    """Map SDK/API failures to LLMError so routes return 502 instead of 500."""
    message = str(err).strip() or err.__class__.__name__
    return LLMError(f"{provider} API error: {message}")


def _coerce_string_list(value: Any) -> list[str]:
    """Normalize whatever the LLM returned into a clean list of strings."""
    if value is None:
        return []
    if not isinstance(value, list):
        value = [value]
    return [str(item).strip() for item in value if str(item).strip()]
