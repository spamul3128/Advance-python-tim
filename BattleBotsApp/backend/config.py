"""Centralized application configuration loaded from environment variables.

All env variables documented in `.env.example`. Importing `settings` from this
module is the canonical way to access config throughout the codebase — never
read environment variables directly elsewhere.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the backend/ directory at import time so paths in env vars can be
# specified relative to it (e.g. DATABASE_PATH=data/battlebots.db).
BACKEND_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Strongly-typed settings backed by environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Bright Data ---
    brightdata_api_token: str = Field(default="", description="Bright Data API token")
    brightdata_web_unlocker_zone: str = Field(default="battlebots_unlocker")
    brightdata_country: str = Field(default="us")
    brightdata_timeout_seconds: int = Field(default=90, ge=10, le=300)

    # --- Storage ---
    database_path: str = Field(default="data/battlebots.db")

    # --- LLM ---
    llm_provider: Literal["openai", "anthropic"] = Field(default="openai")
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-5.4")
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514")

    # --- Scraper behavior ---
    scraper_request_delay_seconds: float = Field(default=1.5, ge=0.0, le=60.0)
    sentiment_max_quotes: int = Field(default=50, ge=1, le=500)
    reddit_search_limit: int = Field(default=100, ge=25, le=100)
    reddit_search_pages: int = Field(default=2, ge=1, le=5)
    reddit_comment_posts: int = Field(default=12, ge=0, le=50)
    reddit_max_comments_per_post: int = Field(default=30, ge=0, le=200)
    reddit_subreddits: str = Field(default="Battlebots,robotwars")
    log_level: str = Field(default="INFO")

    # --- RAG (Reddit sentiment retrieval) ---
    rag_enabled: bool = Field(default=True)
    embedding_model: str = Field(default="text-embedding-3-small")
    rag_top_k_per_bot: int = Field(default=8, ge=1, le=30)

    @property
    def reddit_subreddit_list(self) -> list[str]:
        return [s.strip() for s in self.reddit_subreddits.split(",") if s.strip()]

    @property
    def database_full_path(self) -> Path:
        """Absolute path to the SQLite database file."""
        db_path = Path(self.database_path)
        if not db_path.is_absolute():
            db_path = BACKEND_DIR / db_path
        return db_path

    def require_brightdata(self) -> None:
        """Raise if Bright Data credentials are not configured."""
        if not self.brightdata_api_token:
            raise RuntimeError(
                "BRIGHTDATA_API_TOKEN is not set. Populate backend/.env "
                "with your Bright Data credentials before running scrapers."
            )
        if not self.brightdata_web_unlocker_zone:
            raise RuntimeError(
                "BRIGHTDATA_WEB_UNLOCKER_ZONE is not set. Populate backend/.env."
            )

    def can_embed(self) -> bool:
        """True when OpenAI embeddings are available for RAG indexing."""
        return bool(self.openai_api_key) and self.rag_enabled


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a singleton Settings instance."""
    return Settings()


settings = get_settings()
