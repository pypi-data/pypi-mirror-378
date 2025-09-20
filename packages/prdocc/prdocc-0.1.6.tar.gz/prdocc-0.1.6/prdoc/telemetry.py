from __future__ import annotations

import os
import time
import uuid
import warnings
from dataclasses import dataclass, field
from importlib import metadata
from typing import Any, Callable, Dict, Optional, Protocol

_WARN_STACKLEVEL = 2

# ---- Basics -----------------------------------------------------------------


def _env_truthy(key: str) -> bool:
    val = os.environ.get(key, "")
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_version() -> str:
    try:
        return metadata.version("prdoc")
    except Exception:
        return "0.0.0"


# ---- Transport --------------------------------------------------------------


class Transport(Protocol):
    def send(self, url: str, payload: Dict[str, Any], timeout: int) -> None: ...


class RequestsTransport:
    """Best-effort HTTP transport; silently ignores network errors."""

    def __init__(self) -> None:
        try:
            import requests  # local import to avoid hard dep at import time
        except Exception as err:  # pragma: no cover
            warnings.warn(
                f"Telemetry disabled: requests not available ({err})",
                category=UserWarning,
                stacklevel=_WARN_STACKLEVEL,
            )
            self._requests = None
        else:
            self._requests = requests

    def send(
        self, url: str, payload: Dict[str, Any], timeout: int
    ) -> None:  # pragma: no cover (exercised in prod)
        if self._requests is None:
            return
        try:
            self._requests.post(url, json=payload, timeout=timeout)
        except Exception:
            # Never crash user workflows due to telemetry.
            return


class NoopTransport:
    def send(self, url: str, payload: Dict[str, Any], timeout: int) -> None:
        return


# ---- Client -----------------------------------------------------------------

_PII_KEYS = {
    "repo",
    "repository",
    "user",
    "username",
    "email",
    "token",
    "apikey",
    "api_key",
    "password",
}
_MAX_STRING = 2048
_MAX_LIST = 100


def _sanitize(value: Any) -> Any:
    """Make values JSON-friendly and small."""
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if isinstance(value, str):
        if len(value) > _MAX_STRING:
            return value[:_MAX_STRING] + "…"
        return value
    if isinstance(value, dict):
        return {str(k): _sanitize(v) for k, v in value.items() if str(k) not in _PII_KEYS}
    if isinstance(value, (list, tuple, set)):
        out = list(value)[:_MAX_LIST]
        return [_sanitize(v) for v in out]
    # Fallback to string
    s = str(value)
    if len(s) > _MAX_STRING:
        s = s[:_MAX_STRING] + "…"
    return s


def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    out.update(b)
    return out


@dataclass
class TelemetryClient:
    enabled: bool = False
    endpoint: str = "https://telemetry.prdoc.dev/v1/events"
    timeout_s: int = 2
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    transport: Transport = field(default_factory=NoopTransport)
    # Clocks for easy testing
    now_ms: Callable[[], int] = field(default=_now_ms)
    perf_clock: Callable[[], float] = field(default=time.perf_counter)

    common: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls, *, transport: Optional[Transport] = None) -> "TelemetryClient":
        enabled = _env_truthy("PRDOC_TELEMETRY")  # opt-in only
        endpoint = os.environ.get("PRDOC_TELEMETRY_URL", "https://telemetry.prdoc.dev/v1/events")
        timeout = int(os.environ.get("PRDOC_TELEMETRY_TIMEOUT", "2"))
        t = transport or (RequestsTransport() if enabled else NoopTransport())
        common = {
            "lib": "prdoc",
            "lib_version": _safe_version(),
            "python": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            "platform": os.name,
        }
        return cls(
            enabled=enabled,
            endpoint=endpoint,
            timeout_s=timeout,
            transport=t,
            common=common,
        )

    # ---- API ----

    def track(self, event: str, **props: Any) -> bool:
        if not self.enabled:
            return False
        payload: Dict[str, Any] = {
            "event": event,
            "ts": self.now_ms(),
            "session_id": self.session_id,
            "props": _sanitize(_merge(self.common, props)),
        }
        try:
            self.transport.send(self.endpoint, payload, self.timeout_s)
        except Exception:  # pragma: no cover (NoopTransport never raises)
            return False
        return True

    def timed(self, event: str, **props: Any):
        """Context manager to record a duration in milliseconds with 'duration_ms' prop."""
        client = self
        start = self.perf_clock()

        class _Timer:
            def __enter__(self, *a, **k):  # noqa: ANN001
                return None

            def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
                dur_ms = int(round((client.perf_clock() - start) * 1000))
                ok = exc is None
                # Never include exception text; boolean is enough for telemetry.
                ev_props = dict(props)
                ev_props["duration_ms"] = dur_ms
                ev_props["ok"] = ok
                client.track(event, **ev_props)
                # Do not swallow exceptions
                return False

        return _Timer()

    # Convenience: summarize patch counts
    def track_patch_summary(self, *, files: int, patches: int) -> bool:
        return self.track("patch_summary", files=int(files), patches=int(patches))
