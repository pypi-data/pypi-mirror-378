import re
from pathlib import Path
from typing import Dict, List, Set


class TrigramSearchIndex:
    def __init__(self) -> None:
        self.index: Dict[str, Set[Path]] = {}
        self.contents: Dict[Path, str] = {}

    def _trigrams(self, text: str) -> Set[str]:
        normalized = re.sub(r"\s+", " ", text.lower())
        return {normalized[i : i + 3] for i in range(len(normalized) - 2)}

    def add_file(self, path: Path, text: str) -> None:
        self.contents[path] = text
        trigrams = self._trigrams(text)
        for tri in trigrams:
            self.index.setdefault(tri, set()).add(path)

    def query(self, text: str, threshold: float = 0.5) -> List[Path]:
        query_tris = self._trigrams(text)
        scores: Dict[Path, int] = {}

        for tri in query_tris:
            for path in self.index.get(tri, []):
                scores[path] = scores.get(path, 0) + 1

        if not scores:
            return []

        max_score = max(scores.values())
        min_required = int(max_score * threshold)

        return [path for path, score in scores.items() if score >= min_required]
