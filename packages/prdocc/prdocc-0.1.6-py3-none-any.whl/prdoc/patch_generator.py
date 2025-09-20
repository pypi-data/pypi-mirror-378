# prdoc/patch_generator.py
from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Iterable, List, Optional, Protocol


class SupportsComplete(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass(frozen=True)
class DocHit:
    """
    Minimal representation of a documentation search hit.

    Attributes
    ----------
    path : str
        Repository-relative file path of the document to patch.
    text : str
        Current on-disk contents of the document.
    """

    path: str
    text: str


@dataclass(frozen=True)
class PatchResult:
    """
    Output of the patch generator for a single document.

    Attributes
    ----------
    path : str
        Repository-relative file path that the patch modifies.
    patch : str
        Unified diff (GNU patch-compatible) representing changes
        from the original content to the updated content.
    updated_text : str
        The full updated file content returned by the LLM.
    """

    path: str
    patch: str
    updated_text: str


SYSTEM_PROMPT = (
    "You are a documentation auto-editor. You receive the current contents of a file and "
    "an instruction. Return the FULL, updated file contents (not a diff). Keep formatting, "
    "frontmatter, and code blocks intact. If the instruction does not require changes, "
    "return the original content exactly."
)


def _build_user_prompt(file_path: str, instruction: str, current_text: str) -> str:
    # Using XML-ish guards keeps models from dropping or hallucinating headers.
    return (
        f"Target file: {file_path}\n\n"
        f"Instruction:\n{instruction}\n\n"
        f"<CURRENT_FILE>\n{current_text}\n</CURRENT_FILE>\n\n"
        "Return ONLY the full updated file content."
    )


def make_unified_diff(old_text: str, new_text: str, path: str) -> str:
    """
    Produce a unified diff between two full file texts.

    Parameters
    ----------
    old_text : str
        Original file content.
    new_text : str
        Updated file content.
    path : str
        Repo-relative file path (used in diff headers).

    Returns
    -------
    str
        Unified diff string ('' if no changes).
    """
    if old_text == new_text:
        return ""

    # Ensure trailing newline behavior is stable
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff_iter = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        lineterm="\n",
        n=3,  # context lines
    )
    return "".join(diff_iter)


class PatchGenerator:
    """
    Generates unified diff patches for doc hits by querying an LLM for the updated file content.
    """

    def __init__(self, llm: SupportsComplete):
        self._llm = llm

    def generate_for_hit(
        self,
        hit: DocHit,
        instruction: str,
        system_prompt: Optional[str] = None,
    ) -> Optional[PatchResult]:
        """
        Generate a patch for a single DocHit. Returns None if no changes are required.

        Parameters
        ----------
        hit : DocHit
            The documentation item to update.
        instruction : str
            Natural-language instruction describing desired changes (e.g., “update CLI usage for --no-verify”).
        system_prompt : Optional[str]
            Override the default system prompt (mainly for testing).

        Returns
        -------
        Optional[PatchResult]
        """
        sys = system_prompt or SYSTEM_PROMPT
        user = _build_user_prompt(hit.path, instruction, hit.text)

        updated = self._llm.complete(system=sys, user=user).rstrip("\n")
        # Normalize both ends the same way to prevent spurious diffs on trailing newlines
        original = hit.text.rstrip("\n")

        # Restore single trailing newline to both (POSIX text file convention)
        if original != "":
            original += "\n"
        if updated != "":
            updated += "\n"

        patch = make_unified_diff(original, updated, hit.path)
        if not patch:
            return None

        return PatchResult(path=hit.path, patch=patch, updated_text=updated)

    def generate_for_hits(
        self, hits: Iterable[DocHit], instruction: str, system_prompt: Optional[str] = None
    ) -> List[PatchResult]:
        """
        Batch variant over an iterable of DocHit.

        Returns only entries that actually change (no-ops are filtered out).
        """
        results: List[PatchResult] = []
        for h in hits:
            res = self.generate_for_hit(h, instruction, system_prompt=system_prompt)
            if res is not None:
                results.append(res)
        return results
