from __future__ import annotations

from pathlib import Path

from dotenv import find_dotenv, load_dotenv


def load_env() -> None:
    """
    Load environment variables from a `.env` file in the current directory,
    without overriding existing shell/CI variables.
    """
    env_path = find_dotenv(usecwd=True)
    if env_path:
        load_dotenv(dotenv_path=env_path, override=False)
    else:
        fallback = Path.cwd() / ".env"
        if fallback.exists():
            load_dotenv(dotenv_path=fallback, override=False)
