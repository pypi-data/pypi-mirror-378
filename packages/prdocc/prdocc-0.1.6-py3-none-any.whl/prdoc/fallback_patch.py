from __future__ import annotations

import difflib
import re
from typing import List, Tuple

_HEURISTICS: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bteh\b", re.IGNORECASE), "the"),
    (re.compile(r"\brecieve\b", re.IGNORECASE), "receive"),
    (re.compile(r"[ \t]+$", re.MULTILINE), ""),  # trim trailing whitespace
    (re.compile(r"\r\n"), "\n"),  # normalize newlines
    (re.compile(r"[ \t]{2,}"), " "),  # collapse runs of spaces/tabs
]


def apply_heuristics(text: str) -> str:
    out = text
    for pat, repl in _HEURISTICS:
        out = pat.sub(repl, out)
    return out


def fallback_patch(original_text: str) -> str:
    """
    Generate a simple unified diff by applying text heuristics.
    Returns empty string if no changes are suggested.
    """
    updated = apply_heuristics(original_text)
    if updated == original_text:
        return ""
    diff = difflib.unified_diff(
        original_text.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile="a/docs.md",
        tofile="b/docs.md",
        lineterm="",
    )
    return "".join(diff)
