"""Caching for analysis results."""

import hashlib
import json
import os
from pathlib import Path


def cache_key(
    repo_head: str,
    rel_file_path: str,
    line_start: int | None,
    line_end: int | None,
    question: str | None,
    max_commits: int,
    use_llm: bool,
) -> str:
    """
    Generate a cache key from parameters.

    Args:
        repo_head: HEAD commit hash
        rel_file_path: Relative file path
        line_start: Start line
        line_end: End line
        question: Optional question
        max_commits: Max commits
        use_llm: Whether to use LLM

    Returns:
        SHA256 hash as hex string
    """
    key_str = f"{repo_head}:{rel_file_path}:{line_start}:{line_end}:{question}:{max_commits}:{use_llm}"
    return hashlib.sha256(key_str.encode()).hexdigest()


def cache_get(repo_cache_dir: str, key: str) -> dict | None:
    """
    Get cached analysis result.

    Args:
        repo_cache_dir: Cache directory path
        key: Cache key

    Returns:
        Cached data or None if not found
    """
    cache_file = os.path.join(repo_cache_dir, f"{key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def cache_set(repo_cache_dir: str, key: str, payload_dict: dict) -> None:
    """
    Store analysis result in cache.

    Args:
        repo_cache_dir: Cache directory path
        key: Cache key
        payload_dict: Data to cache
    """
    os.makedirs(repo_cache_dir, exist_ok=True)
    cache_file = os.path.join(repo_cache_dir, f"{key}.json")
    try:
        with open(cache_file, "w") as f:
            json.dump(payload_dict, f, indent=2)
    except Exception:
        # Silently fail on cache write errors
        pass
