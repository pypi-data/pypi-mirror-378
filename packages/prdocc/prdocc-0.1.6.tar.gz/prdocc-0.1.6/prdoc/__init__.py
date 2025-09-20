# prdoc/__init__.py
from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

__all__ = ["app", "__version__"]

# Expose CLI app for console entry points and imports
from .cli import app  # noqa: E402

# Package version (falls back in editable/dev installs)
try:
    __version__ = _pkg_version("prdoc")
except PackageNotFoundError:
    __version__ = "0.0.0"
