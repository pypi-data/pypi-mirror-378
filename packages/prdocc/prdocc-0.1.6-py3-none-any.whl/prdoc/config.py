# prdoc/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping, Optional

# Optional YAML support
try:
    import yaml as _yaml  # type: ignore
except Exception:  # pragma: no cover
    _yaml = None


# Public dataclasses & loaders


@dataclass
class Settings:
    """
    Authentication & provider tokens (sourced from environment).
    """

    github_token: Optional[str]
    llm_provider: Optional[str]
    groq_api_key: Optional[str]
    openai_api_key: Optional[str]


def load_settings(env: Optional[Mapping[str, str]] = None) -> Settings:
    """
    Load API tokens from environment variables.
      - GITHUB_TOKEN
      - PRDOC_LLM_PROVIDER   (alias for provider; see Config for richer precedence)
      - GROQ_API_KEY
      - OPENAI_API_KEY
    """
    env = env or os.environ
    return Settings(
        github_token=env.get("GITHUB_TOKEN"),
        llm_provider=env.get("PRDOC_LLM_PROVIDER"),
        groq_api_key=env.get("GROQ_API_KEY"),
        openai_api_key=env.get("OPENAI_API_KEY"),
    )


@dataclass
class Config:
    """
    Repo-scoped runtime configuration (with precedence):
      defaults < .prdoc.yaml/.yml < PRDOC_* env
    CLI flags are applied in cli.py on top of this (highest precedence).
    """

    provider: str = "openai"
    model: Optional[str] = None
    verbose: bool = False


def load_config(start: Optional[Path] = None, env: Optional[Mapping[str, str]] = None) -> Config:
    """
    Resolve effective configuration from:
      1) defaults
      2) nearest .prdoc.yaml/.yml upwards from `start` (or CWD)
      3) environment (PRDOC_PROVIDER/PRDOC_LLM_PROVIDER, PRDOC_MODEL, PRDOC_VERBOSE)
    """
    start = start or Path.cwd()
    env = env or os.environ
    defaults = Config()
    file_cfg = _load_file_config(start)
    env_cfg = _load_env_config(env)
    return merge(defaults, file_cfg, env_cfg)


# Internal helpers


def merge(base: Config, file_cfg: Dict[str, object], env_cfg: Dict[str, object]) -> Config:
    """
    Precedence: defaults < file < env.
    """
    cfg = Config(**vars(base))

    # Apply file, then env
    for src in (file_cfg, env_cfg):
        if "provider" in src and src["provider"]:
            cfg.provider = str(src["provider"])
        if "model" in src:
            v = src["model"]
            cfg.model = str(v) if v not in (None, "") else None
        if "verbose" in src:
            cfg.verbose = bool(src["verbose"])

    return cfg


def _load_file_config(start: Path) -> Dict[str, object]:
    """
    Find and parse .prdoc.yaml/.yml walking up from `start`.
    Recognized keys: provider (alias: llm_provider), model, verbose.
    """
    p = _find_config_file(start)
    if not p:
        return {}
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return {}

    data = _parse_yaml_text(text)
    if not isinstance(data, dict):
        return {}

    out: Dict[str, object] = {}

    # Accept aliases and normalize
    provider = data.get("provider")
    if provider in (None, ""):
        provider = data.get("llm_provider")
    if provider not in (None, ""):
        out["provider"] = str(provider)

    model = data.get("model")
    if model not in (None, ""):
        out["model"] = str(model)

    if "verbose" in data:
        out["verbose"] = _as_bool(data.get("verbose"))

    return out


def _load_env_config(env: Mapping[str, str]) -> Dict[str, object]:
    """
    Read configuration from environment:
      - PRDOC_PROVIDER or PRDOC_LLM_PROVIDER
      - PRDOC_MODEL
      - PRDOC_VERBOSE (1/true/yes/on)
    """
    out: Dict[str, object] = {}

    prov = (env.get("PRDOC_PROVIDER") or env.get("PRDOC_LLM_PROVIDER") or "").strip()
    if prov:
        out["provider"] = prov

    model = (env.get("PRDOC_MODEL") or "").strip()
    if model:
        out["model"] = model

    verb = env.get("PRDOC_VERBOSE")
    if verb is not None:
        out["verbose"] = _as_bool(verb)

    return out


def _find_config_file(start: Path) -> Optional[Path]:
    """
    Search upward from `start` for .prdoc.yaml or .prdoc.yml and return the first found.
    """
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent

    while True:
        for name in (".prdoc.yaml", ".prdoc.yml"):
            cand = cur / name
            if cand.exists() and cand.is_file():
                return cand
        if cur.parent == cur:
            return None
        cur = cur.parent


def _parse_yaml_text(text: str) -> object:
    """
    Parse YAML if pyyaml is available, otherwise fall back to a minimal "key: value" parser.
    """
    if _yaml is not None:
        try:
            return _yaml.safe_load(text) or {}
        except Exception:
            return {}

    # Fallback: extremely small subset (lines like "key: value")
    result: Dict[str, object] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        val = v.strip().strip('"').strip("'")
        # naive boolean detection for fallback
        if val.lower() in ("true", "yes", "on"):
            result[key] = True
        elif val.lower() in ("false", "no", "off"):
            result[key] = False
        else:
            result[key] = val
    return result


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    s = str(value).strip().lower()
    return s in ("1", "true", "yes", "on")
