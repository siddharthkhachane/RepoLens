"""Tests for git command runner."""

import pytest
from app.services.git_runner import run_git, GitCommandError


def test_run_git_success(temp_git_repo):
    """Test successful git command execution."""
    output = run_git(temp_git_repo["path"], ["rev-parse", "HEAD"])
    assert output.strip()
    assert len(output.strip()) == 40  # Hash should be 40 chars


def test_run_git_failure(temp_git_repo):
    """Test that git command failure raises GitCommandError."""
    with pytest.raises(GitCommandError):
        run_git(temp_git_repo["path"], ["invalid-command"])


def test_run_git_log(temp_git_repo):
    """Test git log command."""
    output = run_git(temp_git_repo["path"], ["log", "--oneline"])
    lines = output.strip().split("\n")
    assert len(lines) >= 3  # We created 3 commits
