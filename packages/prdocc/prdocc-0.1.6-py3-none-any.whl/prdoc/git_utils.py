import subprocess
from pathlib import Path
from typing import Optional


def run_git(args: list[str], cwd: Optional[Path] = None) -> str:
    """Run a git command and return stdout as string. Raises on failure."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def clone_repo(repo_url: str, dest_dir: Path) -> None:
    """Clones the repo to a destination directory."""
    run_git(["clone", repo_url, str(dest_dir)])


def checkout_pr(pr_number: int, repo_dir: Path) -> None:
    """Fetch and checkout a pull request as a local branch."""
    run_git(["fetch", "origin", f"pull/{pr_number}/head:pr-{pr_number}"], cwd=repo_dir)
    run_git(["checkout", f"pr-{pr_number}"], cwd=repo_dir)


def get_diff(repo_dir: Path, base: str = "main", head: str = "HEAD") -> str:
    """Returns the unified diff between base and head."""
    return run_git(["diff", f"{base}..{head}"], cwd=repo_dir)
