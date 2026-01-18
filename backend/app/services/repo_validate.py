"""Repository validation."""

import os
from .git_runner import run_git, GitCommandError


def validate_repo(repo_path: str) -> tuple[bool, str | None]:
    """
    Validate that a path is a git repository.

    Args:
        repo_path: Path to validate

    Returns:
        Tuple of (is_valid, head_hash)
    """
    if not os.path.exists(repo_path):
        return False, None

    git_dir = os.path.join(repo_path, ".git")
    if not os.path.exists(git_dir):
        return False, None

    try:
        # Check if it's a valid git repo
        run_git(repo_path, ["rev-parse", "--is-inside-work-tree"])

        # Get HEAD hash
        head_hash = run_git(repo_path, ["rev-parse", "HEAD"]).strip()

        return True, head_hash
    except (GitCommandError, Exception):
        return False, None
