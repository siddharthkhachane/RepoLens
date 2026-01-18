"""Tests for repo validation."""

import pytest
from app.services.repo_validate import validate_repo


def test_validate_repo_valid(temp_git_repo):
    """Test that validation works on a valid repo."""
    is_valid, head = validate_repo(temp_git_repo["path"])
    assert is_valid is True
    assert head is not None
    assert len(head) == 40  # Git hash should be 40 hex chars
    assert all(c in "0123456789abcdef" for c in head)


def test_validate_repo_invalid_path():
    """Test that validation fails on non-existent path."""
    is_valid, head = validate_repo("/nonexistent/path")
    assert is_valid is False
    assert head is None


def test_validate_repo_no_git():
    """Test that validation fails on non-git directory."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        is_valid, head = validate_repo(tmpdir)
        assert is_valid is False
        assert head is None
