from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Iterable, List, Optional, Protocol, runtime_checkable

# Where warnings should appear to originate from.
# 2 = caller of _load_plugins (i.e., load_symbol_extractors / load_doc_indexers)
_WARN_STACKLEVEL = 2

# Entry point groups (public constants)
EP_GROUP_SYMBOL_EXTRACTOR = "prdoc.symbol_extractor"
EP_GROUP_DOC_INDEXER = "prdoc.doc_indexer"

# Simple data structures


@dataclass(frozen=True)
class Symbol:
    """A minimal, language-agnostic symbol record."""

    name: str
    kind: str  # e.g., "function", "class", "method", "variable", "module"
    path: str  # file path
    line: int = 0
    col: int = 0
    signature: Optional[str] = None
    doc: Optional[str] = None


@dataclass(frozen=True)
class DocHit:
    """A search result returned by a DocIndexer."""

    path: str
    score: float
    snippet: Optional[str] = None


# Plugin protocols (runtime-checkable)


@runtime_checkable
class SymbolExtractor(Protocol):
    """Plugins that extract symbols from source files for many languages."""

    # A short, stable identifier. Used for filtering.
    name: str

    def languages(self) -> Iterable[str]:
        """Return iterable of language identifiers, e.g., ['python', 'go']."""
        ...

    def extract(self, path: str, content: str) -> List[Symbol]:
        """
        Extract language-specific symbols from a single file.
        Return a list of Symbol records (empty list if none).
        """
        ...


@runtime_checkable
class DocIndexer(Protocol):
    """Plugins that build and query a documentation index."""

    name: str

    def index(self, paths: Iterable[str]) -> int:
        """Index the given doc files. Return count of items indexed."""
        ...

    def search(self, query: str, k: int = 5) -> List[DocHit]:
        """Return top-k results for a free-text query."""
        ...


# Public loader APIs


def load_symbol_extractors() -> List[SymbolExtractor]:
    """Discover and instantiate all enabled SymbolExtractor plugins."""
    return _load_plugins(EP_GROUP_SYMBOL_EXTRACTOR, SymbolExtractor)


def load_doc_indexers() -> List[DocIndexer]:
    """Discover and instantiate all enabled DocIndexer plugins."""
    return _load_plugins(EP_GROUP_DOC_INDEXER, DocIndexer)


# Internals


def _load_plugins(group: str, proto: Any) -> List[Any]:
    # Allow global kill switch for CI or security-sensitive environments.
    if _env_truthy("PRDOC_DISABLE_PLUGINS"):
        return []

    only = _csv_set(os.environ.get("PRDOC_PLUGINS_ONLY", ""))
    exclude = _csv_set(os.environ.get("PRDOC_PLUGINS_EXCLUDE", ""))

    plugins: List[Any] = []
    for ep in _entry_points_for_group(group):
        ep_name = getattr(ep, "name", "<unknown>")
        if only and ep_name not in only:
            continue
        if ep_name in exclude:
            continue

        try:
            obj = ep.load()
        except Exception as err:  # noqa: BLE001
            warnings.warn(
                f"Failed to load plugin {ep_name!r} from {group}: {err}",
                category=UserWarning,
                stacklevel=_WARN_STACKLEVEL,
            )
            continue

        # Accept either a class with no-arg ctor or an already-instantiated object.
        try:
            inst = obj() if isinstance(obj, type) else obj
        except Exception as err:  # noqa: BLE001
            warnings.warn(
                f"Failed to instantiate plugin {ep_name!r}: {err}",
                category=UserWarning,
                stacklevel=_WARN_STACKLEVEL,
            )
            continue

        # Require protocol conformance at runtime to prevent surprises downstream.
        if not isinstance(inst, proto):  # type: ignore[arg-type]
            warnings.warn(
                f"Plugin {ep_name!r} from {group} does not implement required protocol {proto.__name__}",
                category=UserWarning,
                stacklevel=_WARN_STACKLEVEL,
            )
            continue

        # Normalize the plugin's public identifier to the entry-point name so that
        # env filters (ONLY/EXCLUDE), logs, and tests all align on the same ID.
        try:
            inst.name = ep_name
        except Exception:  # pragma: no cover
            warnings.warn(
                f"Plugin {ep_name!r} does not allow setting 'name'; skipping.",
                category=UserWarning,
                stacklevel=_WARN_STACKLEVEL,
            )
            continue

        plugins.append(inst)

    # Sort by entry point name for deterministic order.
    plugins.sort(key=lambda p: getattr(p, "name", ""))
    return plugins


def _entry_points_for_group(group: str):
    """
    Compatibility wrapper for importlib.metadata.entry_points across Python versions.
    Returns an iterable of EntryPoint-like objects with attributes: .name and .load().
    """
    eps = metadata.entry_points()
    # Python 3.10+ provides .select(group=...)
    select = getattr(eps, "select", None)
    if callable(select):
        return select(group=group)
    # Older behavior: mapping-like object or flat list
    if isinstance(eps, dict):
        return eps.get(group, [])
    # Fallback: filter by attribute
    return [ep for ep in eps if getattr(ep, "group", None) == group]


def _env_truthy(key: str) -> bool:
    val = os.environ.get(key, "")
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _csv_set(raw: str) -> set[str]:
    items = [x.strip() for x in raw.split(",") if x.strip()]
    return set(items)
