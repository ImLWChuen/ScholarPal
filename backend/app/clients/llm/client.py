"""
LLM Client Interface for structured extraction from crawled scholarship documents.
Note: In accordance with Non-negotiable Rule 1, LLM output is strictly confined to extraction
and parsing, and is NEVER used to evaluate student eligibility.
"""

from typing import TypeVar

from pydantic import BaseModel

from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL

    async def extract_structured(self, raw_html_or_text: str, response_schema: type[T]) -> T:
        """
        Placeholder interface: Calls LLM API with structured outputs (JSON schema enforcement).
        """
        raise NotImplementedError("LLM structured extraction client will be wired to provider API.")
