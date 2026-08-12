"""OpenAI embedding helpers for the sentiment RAG pipeline."""

from __future__ import annotations

import logging
from typing import Sequence

from openai import OpenAI

from ..config import settings

logger = logging.getLogger(__name__)

_BATCH_SIZE = 64


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns one vector per input string."""
    if not texts:
        return []
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required for RAG embeddings. "
            "Set it in backend/.env or disable RAG with RAG_ENABLED=false."
        )

    client = OpenAI(api_key=settings.openai_api_key)
    vectors: list[list[float]] = []

    for start in range(0, len(texts), _BATCH_SIZE):
        batch = list(texts[start : start + _BATCH_SIZE])
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        ordered = sorted(response.data, key=lambda row: row.index)
        vectors.extend(row.embedding for row in ordered)
        logger.debug("Embedded %d/%d chunks", len(vectors), len(texts))

    return vectors
