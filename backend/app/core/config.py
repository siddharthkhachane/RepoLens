"""RepoLens configuration."""

import os
from functools import lru_cache


class Settings:
    """Application settings from environment variables."""

    openai_api_key: str | None = None
    repolens_cache_dir: str = ".repolens_cache"

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.repolens_cache_dir = os.getenv("REPOLENS_CACHE_DIR", ".repolens_cache")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
