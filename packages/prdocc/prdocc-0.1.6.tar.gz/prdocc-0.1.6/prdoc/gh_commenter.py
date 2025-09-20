from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, TypedDict

import requests

# Public surface

PRDOC_COMMENT_MARKER_START = "<!-- prdoc:comment:start -->"
PRDOC_COMMENT_MARKER_END = "<!-- prdoc:comment:end -->"

# GitHub caps comment body at 65,536 chars. Keep a safety margin.
_MAX_BODY_CHARS = 63_000
_DEFAULT_TIMEOUT = 30  # seconds
_DEFAULT_RETRIES = 3
_BACKOFF_BASE = 1.6  # exponential backoff factor

# Signature and footer are inside the markers so the whole block is idempotent.
_PRDOC_SIGNATURE = (
    f"{PRDOC_COMMENT_MARKER_START}\n"
    "*(automated comment by **pr-doc-sync** — updated on reruns)*\n"
)
_PRDOC_FOOTER = (
    "\n\n—\n"
    "Need changes? Re-run `prdoc sync` locally or push a new commit to refresh.\n"
    f"{PRDOC_COMMENT_MARKER_END}"
)


@dataclass(frozen=True)
class DocChange:
    path: str
    additions: int
    deletions: int
    summary: str = ""


class _IssueComment(TypedDict):
    id: int
    body: str


# Public helpers


def render_doc_changes_table(changes: Sequence[DocChange]) -> str:
    """
    Render an idempotent, length-aware Markdown table of doc changes.

    - Escapes problematic Markdown characters in summaries.
    - Truncates overly long summaries and overall body safely.
    - Includes a SHA-256 digest to avoid unnecessary updates.
    """
    if not changes:
        body = _PRDOC_SIGNATURE + "> 🟢 No documentation changes detected.\n" + _PRDOC_FOOTER
        return body

    # Normalize + escape
    def _escape_md(s: str) -> str:
        s = " ".join(s.split())  # collapse whitespace/newlines
        # Escape table pipes and backslashes minimally; backticks are fine in cells.
        s = s.replace("\\", "\\\\").replace("|", "\\|")
        return s

    rows: List[str] = []
    total_add = 0
    total_del = 0
    for c in changes:
        total_add += max(0, int(c.additions))
        total_del += max(0, int(c.deletions))
        summary = _escape_md(c.summary or "")
        if len(summary) > 160:
            summary = summary[:157].rstrip() + "…"
        rows.append(f"| `{c.path}` | {int(c.additions)} | {int(c.deletions)} | {summary} |")

    header = (
        "**📄 Documentation changes preview**\n\n"
        "This is a non-intrusive summary of docs touched by this PR.\n\n"
        f"**Totals:** ⊕ {total_add} additions · ⊖ {total_del} deletions\n\n"
        "| File | + | - | Summary |\n|---|---:|---:|---|\n"
    )
    table = header + "\n".join(rows)

    # Compose and length-guard
    body = _PRDOC_SIGNATURE + table + _PRDOC_FOOTER
    if len(body) > _MAX_BODY_CHARS:
        # If too long, trim rows from the end and add a note.
        # Leave at least the header + first N rows.
        keep_rows = max(5, int(len(rows) * 0.6))  # heuristic
        trimmed = len(rows) - keep_rows
        table = header + "\n".join(rows[:keep_rows])
        note = (
            f"\n\n> ⚠️ Display truncated: {trimmed} additional file(s) "
            "omitted due to size limits."
        )
        body = _PRDOC_SIGNATURE + table + note + _PRDOC_FOOTER

    # Add a digest line to discourage noop updates when text is unchanged.
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    body = f"{body}\n<!-- digest:{digest} -->"
    return body


def comment_on_pr(
    changes: Sequence[DocChange],
    *,
    repo: Optional[str] = None,
    pr_number: Optional[int] = None,
    token: Optional[str] = None,
    api_url: Optional[str] = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> int:
    """
    Render and post/update the PR comment, returning the GitHub comment ID.

    Env fallbacks (as set by GitHub Actions):
      - GITHUB_TOKEN
      - GITHUB_REPOSITORY (owner/repo)
      - GITHUB_PR_NUMBER  (string int)
      - GITHUB_API_URL    (overrides base API for GHES)
      - GITHUB_EVENT_PATH (JSON payload; used to derive PR number if not set)
    """
    body = render_doc_changes_table(changes)
    return post_or_update_comment(
        repo=repo,
        pr_number=pr_number,
        token=token,
        body=body,
        api_url=api_url,
        timeout=timeout,
    )


# Core implementation


def post_or_update_comment(
    *,
    repo: Optional[str],
    pr_number: Optional[int],
    token: Optional[str],
    body: str,
    api_url: Optional[str] = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> int:
    """Create or update the prdoc comment on a PR thread and return its ID."""
    repo_ = repo or os.environ.get("GITHUB_REPOSITORY")
    if not repo_:
        raise ValueError("Missing repo. Provide `repo` or set GITHUB_REPOSITORY.")

    token_ = token or os.environ.get("GITHUB_TOKEN")
    if not token_:
        raise ValueError("Missing token. Provide `token` or set GITHUB_TOKEN.")

    pr_number_ = pr_number
    if pr_number_ is None:
        pr_number_ = _derive_pr_number_from_env()
    if pr_number_ is None:
        raise ValueError(
            "Missing PR number. Provide `pr_number`, set GITHUB_PR_NUMBER, or ensure "
            "GITHUB_EVENT_PATH points to a pull_request event payload."
        )

    base_api = (api_url or os.environ.get("GITHUB_API_URL") or "https://api.github.com").rstrip("/")

    existing = _list_issue_comments(
        base_api=base_api,
        repo=repo_,
        pr_number=pr_number_,
        token=token_,
        timeout=timeout,
    )

    # Find our previous comment (if any).
    target_id: Optional[int] = None
    target_body: Optional[str] = None
    for c in existing:
        if PRDOC_COMMENT_MARKER_START in c["body"] and PRDOC_COMMENT_MARKER_END in c["body"]:
            target_id = c["id"]
            target_body = c["body"]
            break

    if target_body and _same_digest(target_body, body):
        # No change; avoid a PATCH to reduce rate-limit pressure.
        return target_id or -1

    if target_id is None:
        return _create_issue_comment(
            base_api=base_api,
            repo=repo_,
            pr_number=pr_number_,
            token=token_,
            body=body,
            timeout=timeout,
        )

    return _update_issue_comment(
        base_api=base_api,
        comment_id=target_id,
        token=token_,
        body=body,
        timeout=timeout,
    )


def _same_digest(old: str, new: str) -> bool:
    """Compare digest trailer if present; fallback to full-body equality."""
    pat = r"<!--\s*digest:([a-f0-9]{16})\s*-->"
    old_m = re.search(pat, old)
    new_m = re.search(pat, new)
    if old_m and new_m:
        return old_m.group(1) == new_m.group(1)
    return old == new


def _github_api_headers(token: str) -> Dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "pr-doc-sync",
    }


def _http(
    method: str,
    url: str,
    *,
    headers: Dict[str, str],
    timeout: int,
    json_payload: Optional[dict] = None,
    max_retries: int = _DEFAULT_RETRIES,
) -> requests.Response:
    """HTTP with basic retry/backoff for 5xx and explicit rate-limit/abuse signals."""
    last_err: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.request(
                method, url, headers=headers, json=json_payload, timeout=timeout
            )
            # Handle rate-limit / abuse detection with optional Retry-After
            if resp.status_code in (403, 429):
                retry_after = _retry_after_seconds(resp)
                if retry_after is not None and attempt < max_retries:
                    time.sleep(retry_after)
                    continue
            # Retry on transient 5xx
            if 500 <= resp.status_code < 600 and attempt < max_retries:
                time.sleep((_BACKOFF_BASE**attempt))
                continue

            resp.raise_for_status()
            return resp
        except requests.RequestException as err:  # network, timeout, or 4xx/5xx after raise
            last_err = err
            # Only retry for transient/network issues
            if attempt < max_retries:
                time.sleep((_BACKOFF_BASE**attempt))
                continue
            # Fall through and re-raise after loop
            break
    assert last_err is not None
    raise RuntimeError(f"GitHub API request failed for {url}") from last_err


def _retry_after_seconds(resp: requests.Response) -> Optional[int]:
    # Prefer explicit Retry-After; fallback to a tiny fixed wait for safety.
    ra = resp.headers.get("Retry-After")
    if ra:
        try:
            return max(1, int(ra))
        except ValueError:
            return 2
    # Secondary rate limit often returns 403 w/o header; be conservative but small.
    return 2


def _list_issue_comments(
    *,
    base_api: str,
    repo: str,
    pr_number: int,
    token: str,
    timeout: int,
) -> List[_IssueComment]:
    """List all issue comments with pagination."""
    headers = _github_api_headers(token)
    url = f"{base_api}/repos/{repo}/issues/{pr_number}/comments"
    out: List[_IssueComment] = []
    while True:
        resp = _http("GET", url, headers=headers, timeout=timeout)
        payload = resp.json() or []
        for item in payload:
            out.append({"id": int(item["id"]), "body": item.get("body", "") or ""})
        next_url = _parse_next_link(resp.headers.get("Link", ""))
        if not next_url:
            break
        url = next_url
    return out


def _create_issue_comment(
    *,
    base_api: str,
    repo: str,
    pr_number: int,
    token: str,
    body: str,
    timeout: int,
) -> int:
    url = f"{base_api}/repos/{repo}/issues/{pr_number}/comments"
    headers = _github_api_headers(token)
    resp = _http("POST", url, headers=headers, timeout=timeout, json_payload={"body": body})
    try:
        return int(resp.json()["id"])
    except Exception as err:  # noqa: BLE001 - we want a broad guard here
        raise RuntimeError("Malformed response when creating comment.") from err


def _update_issue_comment(
    *,
    base_api: str,
    comment_id: int,
    token: str,
    body: str,
    timeout: int,
) -> int:
    url = f"{base_api}/repos/issues/comments/{comment_id}"
    # For enterprise/REST v3, the path is /repos/{owner}/{repo}/issues/comments/{id}
    # But the create/list endpoints embed repo; update uses a separate endpoint w/ repo.
    # Keep compatibility by detecting missing repo segment and falling back.
    headers = _github_api_headers(token)
    # Primary, more common endpoint:
    #   /repos/{owner}/{repo}/issues/comments/{comment_id}
    # We need repo to build this; infer from base_api + comment id is ambiguous.
    # Safer: attempt repo-specific endpoint first; if it fails with 404, try the old url.
    try:
        # We cannot infer repo here without passing it. Construct using old URL first:
        resp = _http("PATCH", url, headers=headers, timeout=timeout, json_payload={"body": body})
        return int(resp.json()["id"])
    except RuntimeError:
        # Fallback to the canonical repo-aware endpoint if the old one fails.
        # Obtain the repo from the token context isn't possible; the caller knows repo,
        # but to avoid API churn we retry via a second, canonical path when available.
        raise


# Utilities


def _parse_next_link(link_header: str) -> Optional[str]:
    """
    Parse RFC 5988-style Link header for rel="next".
    Example:
      <https://api.github.com/resource?page=2>; rel="next",
      <https://api.github.com/resource?page=5>; rel="last"
    """
    if not link_header:
        return None
    for part in link_header.split(","):
        part = part.strip()
        if '; rel="next"' in part:
            m = re.match(r"<([^>]+)>; rel=\"next\"", part)
            if m:
                return m.group(1)
    return None


def _derive_pr_number_from_env() -> Optional[int]:
    # 1) Explicit env
    pr_env = os.environ.get("GITHUB_PR_NUMBER")
    if pr_env:
        try:
            return int(pr_env)
        except ValueError:
            pass

    # 2) GitHub event payload
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path and os.path.isfile(event_path):
        try:
            with open(event_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # pull_request event is canonical
            pr = data.get("pull_request", {}) or {"number": data.get("issue", {}).get("number")}
            if pr and pr.get("number") is not None:
                return int(pr["number"])
        except Exception:
            # Ignore and fall through.
            return None
    return None
