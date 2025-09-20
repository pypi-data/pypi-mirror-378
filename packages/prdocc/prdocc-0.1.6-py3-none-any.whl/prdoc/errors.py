from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = [
    "PrdocError",
    "ConfigError",
    "GitError",
    "GHError",
    "PluginError",
    "IndexingError",
    "PatchError",
    "LLMError",
    "RateLimitError",
    "BudgetExceededError",
]


@dataclass
class PrdocError(Exception):
    """Base for all prdoc exceptions with structured context."""

    message: str
    code: str = "error"
    context: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.code}: {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        out = {
            "type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "context": dict(self.context) if self.context else {},
        }
        cause = self.__cause__ or self.__context__
        if cause is not None:
            out["cause"] = repr(cause)
        return out

    @classmethod
    def wrap(
        cls,
        message: str,
        *,
        code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[BaseException] = None,
    ) -> "PrdocError":
        """Create an instance chained from a lower-level exception."""
        inst = cls(message=message, code=code or cls.__name__.lower(), context=context or {})
        if cause is not None:
            raise inst from cause
        return inst


class ConfigError(PrdocError):
    pass


class GitError(PrdocError):
    pass


class GHError(PrdocError):
    pass


class PluginError(PrdocError):
    pass


class IndexingError(PrdocError):
    pass


class PatchError(PrdocError):
    pass


class LLMError(PrdocError):
    pass


class RateLimitError(LLMError):
    pass


class BudgetExceededError(LLMError):
    pass
