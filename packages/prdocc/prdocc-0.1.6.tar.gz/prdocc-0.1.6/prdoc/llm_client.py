import logging
import os
from typing import Literal, Optional

import backoff
from openai import APITimeoutError, OpenAI, RateLimitError

logger = logging.getLogger(__name__)

LLMProvider = Literal["openai", "groq"]

DEFAULT_MODEL = "gpt-4"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


def _build_openai_client(api_key: str, base_url: Optional[str] = None) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=base_url)


@backoff.on_exception(backoff.expo, (RateLimitError, APITimeoutError), max_tries=5)
def _retry_completion(client: OpenAI, **kwargs):
    return client.chat.completions.create(**kwargs)


class LLMClient:
    def __init__(
        self,
        provider: LLMProvider = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.provider = provider
        self.model = model or (DEFAULT_GROQ_MODEL if provider == "groq" else DEFAULT_MODEL)

        env_key = "GROQ_API_KEY" if provider == "groq" else "OPENAI_API_KEY"
        self.api_key = api_key or os.getenv(env_key)

        if not self.api_key:
            raise ValueError(f"Missing API key for provider '{provider}'.")

        base_url = (
            "https://api.groq.com/openai/v1" if provider == "groq" else "https://api.openai.com/v1"
        )
        self.client = _build_openai_client(api_key=self.api_key, base_url=base_url)

    def complete(self, system: str, user: str) -> str:
        response = _retry_completion(
            self.client,
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
