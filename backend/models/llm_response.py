"""Standardized response model for provider-independent LLM adapters."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """Normalized model output returned by LLM adapter implementations."""

    content: str = ""
    metadata: dict = field(default_factory=dict)
    provider: str = ""
    model: str = ""
    usage: dict[str, Any] = field(default_factory=dict)

