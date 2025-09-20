import re
from typing import List, Tuple

# Two groups: (1) long flags like --verbose, (2) short flags like -v
FLAG_PATTERN = re.compile(r"(--[\w-]+)|(?<!\w)(-[a-zA-Z])\b")


def extract_flags_from_diff_lines(lines: List[str]) -> Tuple[List[str], List[str]]:
    """
    Given a list of diff lines (with +/- prefix), returns added and removed CLI flags.
    """
    added_flags = []
    removed_flags = []

    for line in lines:
        if line.startswith("+") and not line.startswith("+++"):
            matches = FLAG_PATTERN.findall(line)
            for long_flag, short_flag in matches:
                if long_flag:
                    added_flags.append(long_flag)
                if short_flag:
                    added_flags.append(short_flag)

        elif line.startswith("-") and not line.startswith("---"):
            matches = FLAG_PATTERN.findall(line)
            for long_flag, short_flag in matches:
                if long_flag:
                    removed_flags.append(long_flag)
                if short_flag:
                    removed_flags.append(short_flag)

    return added_flags, removed_flags
