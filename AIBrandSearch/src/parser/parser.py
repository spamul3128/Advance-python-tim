"""
Combines mention extraction and shape classification
into a single parse_result() that returns ParsedSignals.
"""

from src.models import LLMResult, ParsedSignals
from .mention_extractor import extract_mentions
from .shape_classifier import classify_answer_shape


def parse_result(llm_result: LLMResult, tracking_keywords: list[str]) -> ParsedSignals:
    """
    Extract all signals from an LLMResult and return a ParsedSignals object.
    """
    text = llm_result.answer_text or ""
    mentioned_tools, mention_positions = extract_mentions(text, tracking_keywords)
    answer_shape = classify_answer_shape(text)
    word_count = len(text.split()) if text else 0
    summary = (text[:200] + "…") if len(text) > 200 else text

    return ParsedSignals(
        model_name=llm_result.model_name,
        mentioned_tools=mentioned_tools,
        mention_positions=mention_positions,
        answer_shape=answer_shape,
        word_count=word_count,
        summary=summary,
    )
