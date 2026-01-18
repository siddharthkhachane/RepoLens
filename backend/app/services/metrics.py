"""Metrics calculation."""

from .git_runner import run_git


def file_metrics(repo_path: str, rel_file_path: str) -> dict:
    """
    Calculate metrics for a file.

    Args:
        repo_path: Root of the git repository
        rel_file_path: Relative path to file

    Returns:
        Dictionary with churn_count, last_touch, and stability
    """
    # Get commits in last 50
    try:
        output = run_git(
            repo_path,
            ["log", "--pretty=format:%H", "--max-count=50", "--", rel_file_path],
        )
        commits = [h.strip() for h in output.strip().split("\n") if h.strip()]
        churn_count = len(commits)
    except Exception:
        churn_count = 0

    # Get last touch date
    try:
        last_touch = run_git(
            repo_path,
            ["log", "-1", "--pretty=format:%ad", "--date=iso-strict", "--", rel_file_path],
        ).strip()
    except Exception:
        last_touch = None

    # Determine stability
    if churn_count <= 3:
        stability = "stable"
    elif churn_count <= 10:
        stability = "active"
    else:
        stability = "volatile"

    return {
        "churn_count": churn_count,
        "last_touch": last_touch,
        "stability": stability,
    }
