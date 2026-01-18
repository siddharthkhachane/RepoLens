"""Git command runner."""

import subprocess


class GitCommandError(Exception):
    """Raised when a git command fails."""

    def __init__(self, message: str, stderr: str = ""):
        self.message = message
        self.stderr = stderr
        super().__init__(f"{message}\n{stderr}")


def run_git(repo_path: str, args: list[str], timeout_sec: int = 10) -> str:
    """
    Run a git command in the specified repository.

    Args:
        repo_path: Path to the git repository
        args: Git command arguments (e.g., ["log", "--oneline"])
        timeout_sec: Timeout in seconds

    Returns:
        stdout output as string

    Raises:
        GitCommandError: If the command fails
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        if result.returncode != 0:
            raise GitCommandError(
                f"Git command failed: {' '.join(args)}", result.stderr
            )
        return result.stdout
    except subprocess.TimeoutExpired as e:
        raise GitCommandError(f"Git command timed out: {' '.join(args)}") from e
    except FileNotFoundError as e:
        raise GitCommandError("Git command not found") from e
