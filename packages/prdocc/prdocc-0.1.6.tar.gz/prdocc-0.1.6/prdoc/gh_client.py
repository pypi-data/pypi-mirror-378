import os
from typing import Any, Dict, Optional

from github import Github
from github.PullRequest import PullRequest


class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        token = token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GitHub token must be provided or set via GITHUB_TOKEN env var")

        self.gh = Github(token)

    def get_pull_request(self, repo_full_name: str, pr_number: int) -> PullRequest:
        """Fetch a pull request object from a repo like 'owner/repo'."""
        repo = self.gh.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        return pr

    def get_pr_metadata(self, repo_full_name: str, pr_number: int) -> Dict[str, Any]:
        """Returns title, body, changed files, base/head refs."""
        pr = self.get_pull_request(repo_full_name, pr_number)
        return {
            "title": pr.title,
            "body": pr.body,
            "number": pr.number,
            "base": pr.base.ref,
            "head": pr.head.ref,
            "user": pr.user.login,
            "changed_files": [f.filename for f in pr.get_files()],
        }
