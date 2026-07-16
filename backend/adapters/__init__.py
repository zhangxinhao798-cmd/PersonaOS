"""Provider-independent adapter boundaries for PersonaOS runtime intelligence."""

from backend.adapters.registry import AdapterRegistry
from backend.adapters.llm import BaseLLMAdapter
from backend.adapters.ollama import (
    OllamaAdapter,
    OllamaAdapterError,
    OllamaResponseError,
    OllamaTransportError,
)
