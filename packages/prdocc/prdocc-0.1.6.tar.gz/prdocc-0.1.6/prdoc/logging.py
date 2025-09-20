from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as rich_install


def setup_logging(*, verbose: bool = False) -> logging.Logger:
    """Configure Rich logging. Idempotent across repeated calls."""
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("prdoc")
    if getattr(logger, "_prdoc_configured", False):
        logger.setLevel(level)
        return logger

    rich_install(show_locals=False, width=120, word_wrap=True)

    handler = RichHandler(
        rich_tracebacks=True,
        show_path=False,
        show_time=True,
        markup=True,
        console=Console(),
    )
    handler.setLevel(level)

    fmt = logging.Formatter("%(message)s")
    handler.setFormatter(fmt)

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    logger._prdoc_configured = True  # type: ignore[attr-defined]
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("prdoc")


def log_ex(exc: BaseException, *, level: int = logging.ERROR) -> None:
    """Log an exception with structured details when available."""
    logger = get_logger()
    if hasattr(exc, "to_dict"):
        logger.log(level, "%s", exc.to_dict())
    else:
        logger.log(level, "%s", repr(exc))
