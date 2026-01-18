"""Evidence collector from git blame and commit history."""

import os
from pathlib import Path
from .git_runner import run_git
from ..models import CommitEvidence


def resolve_file_path(repo_path: str, file_path: str) -> tuple[str, str]:
    """
    Resolve file path to absolute and relative paths.

    Args:
        repo_path: Root of the git repository
        file_path: File path (relative or absolute)

    Returns:
        Tuple of (absolute_path, relative_path)

    Raises:
        ValueError: If file is not in repo or doesn't exist
    """
    repo_path = os.path.abspath(repo_path)

    # If file_path is absolute, ensure it's in the repo
    if os.path.isabs(file_path):
        abs_path = os.path.abspath(file_path)
    else:
        abs_path = os.path.join(repo_path, file_path)

    abs_path = os.path.abspath(abs_path)

    # Check if file exists
    if not os.path.exists(abs_path):
        raise ValueError(f"File not found: {abs_path}")

    # Ensure file is inside repo
    if not abs_path.startswith(os.path.abspath(repo_path) + os.sep):
        if abs_path != os.path.abspath(repo_path):
            raise ValueError(f"File is not inside repository: {abs_path}")

    # Calculate relative path from repo root
    rel_path = os.path.relpath(abs_path, repo_path)

    return abs_path, rel_path


def get_blame_commits(
    repo_path: str, rel_file_path: str, line_start: int | None, line_end: int | None
) -> list[str]:
    """
    Get commit hashes from git blame.

    Args:
        repo_path: Root of the git repository
        rel_file_path: Relative path to file
        line_start: Start line (1-indexed, optional)
        line_end: End line (1-indexed, optional)

    Returns:
        List of unique commit hashes in order of frequency
    """
    if line_start is None or line_end is None:
        # Get the entire file, but limit to first 200 lines
        try:
            output = run_git(repo_path, ["log", "--pretty=format:%H", rel_file_path])
            hashes = [h.strip() for h in output.strip().split("\n") if h.strip()]
            return hashes[:200]
        except Exception:
            return []

    # Use git blame with line range
    blame_range = f"{line_start},{line_end}"
    try:
        output = run_git(
            repo_path, ["blame", "--porcelain", f"-L{blame_range}", rel_file_path]
        )
    except Exception:
        return []

    # Parse output: each line starts with hash or previous hash marker
    hashes = []
    seen = set()
    for line in output.strip().split("\n"):
        if line.strip():
            # First token is either hash or marker
            parts = line.split()
            if parts:
                token = parts[0]
                # Real hash is 40 hex chars, markers are different
                if len(token) == 40 and all(c in "0123456789abcdef" for c in token):
                    if token not in seen:
                        hashes.append(token)
                        seen.add(token)

    return hashes


def get_commit_details(
    repo_path: str, commit_hash: str, max_diff_chars: int = 2000
) -> CommitEvidence:
    """
    Get details about a single commit.

    Args:
        repo_path: Root of the git repository
        commit_hash: Commit hash
        max_diff_chars: Maximum characters in diff

    Returns:
        CommitEvidence object
    """
    # Get commit info: hash, author, date, subject
    output = run_git(
        repo_path,
        [
            "show",
            "--no-color",
            "-U3",
            "--pretty=format:%H%n%an%n%ad%n%s",
            "--date=iso-strict",
            commit_hash,
        ],
    )

    lines = output.strip().split("\n")
    if len(lines) < 4:
        raise ValueError(f"Could not parse commit details for {commit_hash}")

    commit_hash_retrieved = lines[0]
    author = lines[1]
    date = lines[2]
    subject = lines[3]

    # Get diff snippet
    diff_output = run_git(
        repo_path,
        [
            "show",
            "--no-color",
            "-U3",
            commit_hash,
        ],
    )

    # Truncate diff to max_diff_chars
    diff_snippet = diff_output[: min(len(diff_output), max_diff_chars)]

    return CommitEvidence(
        hash=commit_hash_retrieved,
        author=author,
        date=date,
        subject=subject,
        diff_snippet=diff_snippet,
    )


def collect_evidence(
    repo_path: str,
    rel_file_path: str,
    line_start: int | None,
    line_end: int | None,
    max_commits: int = 10,
) -> list[CommitEvidence]:
    """
    Collect evidence (commits) affecting a file.

    Args:
        repo_path: Root of the git repository
        rel_file_path: Relative path to file
        line_start: Start line (optional)
        line_end: End line (optional)
        max_commits: Maximum number of commits to return

    Returns:
        List of CommitEvidence objects
    """
    # Get blame hashes
    hashes = get_blame_commits(repo_path, rel_file_path, line_start, line_end)

    # Take first max_commits
    hashes = hashes[:max_commits]

    # Fetch details for each
    evidence = []
    for commit_hash in hashes:
        try:
            details = get_commit_details(repo_path, commit_hash)
            evidence.append(details)
        except Exception:
            # Skip commits we can't get details for
            continue

    return evidence
