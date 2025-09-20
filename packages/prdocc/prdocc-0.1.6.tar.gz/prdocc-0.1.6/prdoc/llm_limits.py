from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .errors import BudgetExceededError, RateLimitError
from .logging import get_logger


def _per_1k(input_per_1m: float, output_per_1m: float) -> Tuple[float, float]:
    """
    Convert per-1M token prices to per-1K token prices.
    We store per-1K internally; cost calculation divides tokens by 1000.
    """
    return (round(input_per_1m / 1000.0, 8), round(output_per_1m / 1000.0, 8))


# Prices per 1K tokens: (prompt/input, completion/output).
# Keep legacy entries for backwards compatibility.
_DEFAULT_PRICES: Dict[str, Tuple[float, float]] = {
    # GPT-5 family
    "gpt-5": _per_1k(1.25, 10.00),  # (0.00125, 0.01)
    "gpt-5-mini": _per_1k(0.25, 2.00),  # (0.00025, 0.002)
    "gpt-5-nano": _per_1k(0.05, 0.40),  # (0.00005, 0.0004)
    # Legacy/compat mappings
    "gpt-4o-mini": _per_1k(0.15, 0.60),  # (0.00015, 0.0006)
    # Fallback default for unknown models
    "default": (0.001, 0.002),
}

# Alias resolver so callers can pass various marketing/model names safely.
_MODEL_ALIASES: Dict[str, str] = {
    "chatgpt-latest": "gpt-5",
    "gpt-5-chat-latest": "gpt-5",
    "gpt-5-thinking": "gpt-5",  # maps to standard 5 pricing for budgeting
}


def _resolve_model_key(model: str) -> str:
    return _MODEL_ALIASES.get(model, model)


@dataclass
class LLMUsageGuard:
    """Circuit breaker + budget estimator around LLM calls."""

    max_total_tokens: Optional[int] = None
    max_cost_usd: Optional[float] = None
    rpm: Optional[int] = None  # requests per minute
    rps: Optional[int] = None  # requests per second
    prices_per_1k: Dict[str, Tuple[float, float]] = field(
        default_factory=lambda: dict(_DEFAULT_PRICES)
    )
    clock: Callable[[], float] = time.time
    sleeper: Callable[[float], None] = time.sleep

    used_tokens: int = 0
    used_cost: float = 0.0
    _call_times: List[float] = field(default_factory=list)

    def estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate $ cost for the provided token counts using per-1K pricing.
        """
        key = _resolve_model_key(model)
        pr, cr = self.prices_per_1k.get(key, self.prices_per_1k["default"])
        # tokens are raw counts; convert to 'per 1K' by dividing by 1000
        return (prompt_tokens * pr + completion_tokens * cr) / 1000.0

    def _check_budget(self, est_tokens: int, est_cost: float) -> None:
        if (
            self.max_total_tokens is not None
            and self.used_tokens + est_tokens > self.max_total_tokens
        ):
            raise BudgetExceededError(
                "Token budget exceeded",
                code="budget.tokens",
                context={
                    "limit": self.max_total_tokens,
                    "used": self.used_tokens,
                    "incoming": est_tokens,
                },
            )
        if self.max_cost_usd is not None and self.used_cost + est_cost > self.max_cost_usd:
            raise BudgetExceededError(
                "Cost budget exceeded",
                code="budget.cost",
                context={
                    "limit": self.max_cost_usd,
                    "used": round(self.used_cost, 6),
                    "incoming": round(est_cost, 6),
                },
            )

    def _throttle(self) -> None:
        now = self.clock()
        self._call_times = [t for t in self._call_times if now - t < 60.0]
        # per-minute
        if self.rpm:
            while len([t for t in self._call_times if now - t < 60.0]) >= self.rpm:
                wait = 60.0 - (now - self._call_times[0])
                if wait > 0:
                    self.sleeper(min(wait, 1.0))
                now = self.clock()
                self._call_times = [t for t in self._call_times if now - t < 60.0]
        # per-second
        if self.rps:
            recent = [t for t in self._call_times if now - t < 1.0]
            while len(recent) >= self.rps:
                wait = 1.0 - (now - recent[0])
                if wait > 0:
                    self.sleeper(wait)
                now = self.clock()
                self._call_times = [t for t in self._call_times if now - t < 60.0]
                recent = [t for t in self._call_times if now - t < 1.0]

    def guard_call(
        self,
        fn: Callable[[], Tuple[int, int, object]],
        *,
        model: str = "default",
        prompt_tokens_est: int,
        completion_tokens_est: int,
        max_retries: int = 3,
        backoff: float = 1.6,
    ) -> object:
        """
        Wrap an LLM call with budget check, rate-limit retries, and accounting.

        `fn` should return (prompt_tokens, completion_tokens, result_object).
        """
        logger = get_logger()
        est_cost = self.estimate_cost(model, prompt_tokens_est, completion_tokens_est)
        self._check_budget(prompt_tokens_est + completion_tokens_est, est_cost)

        attempt = 0
        while True:
            self._throttle()
            attempt += 1
            start = self.clock()
            try:
                p_used, c_used, result = fn()
            except RateLimitError:
                if attempt > max_retries:
                    raise
                delay = backoff ** (attempt - 1)
                logger.warning(
                    "LLM rate-limited; retrying",
                    extra={"attempt": attempt, "delay_s": round(delay, 3)},
                )
                self.sleeper(delay)
                continue

            # Successful call
            self._call_times.append(start)
            cost = self.estimate_cost(model, p_used, c_used)
            self.used_tokens += int(p_used + c_used)
            self.used_cost += float(cost)

            logger.info(
                "LLM usage",
                extra={
                    "prompt_toks": p_used,
                    "completion_toks": c_used,
                    "cost_usd": round(cost, 6),
                    "used_tokens": self.used_tokens,
                    "used_cost": round(self.used_cost, 6),
                    "model": _resolve_model_key(model),
                },
            )
            return result
