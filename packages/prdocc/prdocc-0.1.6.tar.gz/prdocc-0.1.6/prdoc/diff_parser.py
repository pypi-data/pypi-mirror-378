import re
from dataclasses import dataclass
from typing import List


@dataclass
class DiffHunk:
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    lines: List[str]


@dataclass
class FileDiff:
    path: str
    hunks: List[DiffHunk]


def parse_unified_diff(diff_text: str) -> List[FileDiff]:
    """
    Parses a unified diff string into a list of FileDiff objects.
    """
    files: List[FileDiff] = []
    current_file: FileDiff | None = None
    current_hunk: DiffHunk | None = None

    diff_lines = diff_text.splitlines()

    hunk_pattern = re.compile(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")

    for line in diff_lines:
        if line.startswith("diff --git"):
            if current_file:
                files.append(current_file)
            current_file = None
            current_hunk = None

        elif line.startswith("--- "):
            continue  # skip old file marker

        elif line.startswith("+++ "):
            path = line[4:].strip()
            current_file = FileDiff(path=path, hunks=[])

        elif line.startswith("@@"):
            match = hunk_pattern.match(line)
            if match and current_file:
                old_start = int(match[1])
                old_len = int(match[2]) if match[2] else 1
                new_start = int(match[3])
                new_len = int(match[4]) if match[4] else 1
                current_hunk = DiffHunk(
                    old_start=old_start,
                    old_lines=old_len,
                    new_start=new_start,
                    new_lines=new_len,
                    lines=[],
                )
                current_file.hunks.append(current_hunk)

        elif current_hunk:
            current_hunk.lines.append(line)

    if current_file:
        files.append(current_file)

    return files
