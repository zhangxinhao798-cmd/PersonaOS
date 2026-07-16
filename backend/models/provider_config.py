"""Provider configuration model for PersonaOS runtime adapters."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderConfig:
    """Provider configuration boundary.

    This model stores configuration only. It does not create adapters, perform
    provider selection, make network requests, or own runtime orchestration.
    """

    provider: str = ""
    model: str = ""
    endpoint: str = ""
    api_key: str | None = None
    options: dict[str, Any] = field(default_factory=dict)

