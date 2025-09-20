from pathlib import Path
from typing import List

DEFAULT_DOC_PATTERNS = ["**/*.md", "**/*.rst", "**/*.mdx"]


def locate_doc_files(root: Path, patterns: List[str] = DEFAULT_DOC_PATTERNS) -> List[Path]:
    """
    Recursively find doc files in the repo matching the given glob patterns.
    Returns a list of Path objects relative to the root.
    """
    matched_files = set()

    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file():
                matched_files.add(path.resolve())

    return sorted(matched_files)
