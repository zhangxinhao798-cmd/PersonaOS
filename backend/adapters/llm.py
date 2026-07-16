"""Provider-independent LLM adapter interface for PersonaOS."""

from abc import ABC, abstractmethod

from backend.models.llm_response import LLMResponse
from backend.models.runtime_context import RuntimeContext


class BaseLLMAdapter(ABC):
    """Common boundary for future model provider adapters.

    Implementations receive an already-assembled RuntimeContext and the raw
    user input for the current turn. Provider-specific adapters are responsible
    for returning a standardized LLMResponse without mutating engine-owned data.
    """

    @abstractmethod
    def generate(
        self,
        runtime_context: RuntimeContext,
        user_input: str,
    ) -> LLMResponse:
        """Generate a standardized response from prepared runtime input."""

