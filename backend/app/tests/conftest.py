"""Test configuration and fixtures."""

import pytest
import tempfile
import os
import subprocess
from pathlib import Path


@pytest.fixture
def temp_git_repo():
    """
    Create a temporary git repository with some commits for testing.

    Returns:
        Dictionary with 'path' and 'file_path' keys
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = tmpdir

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        # Create a test file
        test_file = os.path.join(repo_path, "test.py")
        with open(test_file, "w") as f:
            f.write("# Test file\n")
            f.write("def hello():\n")
            f.write("    return 'world'\n")

        # First commit
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        # Second commit: modify with fix message
        with open(test_file, "w") as f:
            f.write("# Test file\n")
            f.write("def hello():\n")
            f.write("    return 'world fixed'\n")
            f.write("def goodbye():\n")
            f.write("    return 'see you'\n")

        subprocess.run(
            ["git", "add", "test.py"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "fix: resolve issue"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        # Third commit: modify with workaround message
        with open(test_file, "w") as f:
            f.write("# Test file\n")
            f.write("def hello():\n")
            f.write("    return 'world fixed better'\n")
            f.write("def goodbye():\n")
            f.write("    return 'see you later'\n")
            f.write("def wave():\n")
            f.write("    return 'wave'  # workaround for issue #123\n")

        subprocess.run(
            ["git", "add", "test.py"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "workaround: temporary fix"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        yield {"path": repo_path, "file_path": "test.py"}
