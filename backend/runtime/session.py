"""In-memory runtime session boundary for PersonaOS conversations."""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import ClassVar

from backend.models.context import PersonaOSContext
from backend.models.llm_response import LLMResponse
from backend.models.persona_library import PersonaLibraryEntry
from backend.runtime.chat_runtime import (
    ChatRuntime,
    EmptyUserInputError,
)
from backend.runtime.memory_runtime import RuntimeMemoryRetriever


@dataclass
class ConversationTurn:
    """Provider-independent representation of one conversation turn."""

    ALLOWED_ROLES: ClassVar[set[str]] = {"user", "assistant", "system"}

    role: str = "user"
    content: str = ""
    created_at: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.role not in self.ALLOWED_ROLES:
            raise ValueError(f"Unsupported conversation role: {self.role}")
        self.metadata = dict(self.metadata or {})

    def to_dict(self) -> dict:
        """Return a detached provider-independent turn mapping."""

        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "metadata": deepcopy(self.metadata),
        }


class RuntimeSessionError(Exception):
    """Base error for runtime session failures."""


class AssistantResponseError(RuntimeSessionError):
    """Raised when ChatRuntime returns an empty assistant response."""


class RuntimeSessionGenerationError(RuntimeSessionError):
    """Raised when ChatRuntime generation fails during a session turn."""


@dataclass
class RuntimeSession:
    """Own temporary state for one controlled conversation session."""

    id: str
    persona_entry: PersonaLibraryEntry
    persona_os_context: PersonaOSContext
    chat_runtime: ChatRuntime
    memory_retriever: RuntimeMemoryRetriever | None = None
    conversation: list[ConversationTurn] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.metadata = dict(self.metadata or {})

    def send(self, user_input: str) -> LLMResponse:
        """Send one user turn through ChatRuntime.

        Failure policy: the user turn is appended before generation. If
        generation fails, the user turn remains in temporary session history
        with ``metadata["status"] == "failed"`` and no assistant turn is added.
        """

        cleaned_input = self._validate_user_input(user_input)
        user_turn = ConversationTurn(
            role="user",
            content=cleaned_input,
            metadata={"status": "pending"},
        )
        self.conversation.append(user_turn)
        runtime_context = self._context_for_current_turn(user_turn)

        try:
            response = self.chat_runtime.generate_reply(
                cleaned_input,
                self.persona_entry,
                runtime_context,
            )
        except Exception as exc:
            user_turn.metadata["status"] = "failed"
            user_turn.metadata["error"] = "generation_failed"
            self.updated_at = user_turn.created_at
            raise RuntimeSessionGenerationError(
                "Runtime session generation failed."
            ) from exc

        if not isinstance(response.content, str) or not response.content:
            user_turn.metadata["status"] = "failed"
            user_turn.metadata["error"] = "empty_assistant_response"
            self.updated_at = user_turn.created_at
            raise AssistantResponseError("Assistant response content is empty.")

        user_turn.metadata["status"] = "completed"
        assistant_turn = ConversationTurn(
            role="assistant",
            content=response.content,
            metadata={
                "status": "completed",
                "provider": response.provider,
                "model": response.model,
            },
        )
        self.conversation.append(assistant_turn)
        self.updated_at = assistant_turn.created_at
        return response

    def get_history(self) -> list[dict]:
        """Return detached temporary conversation history."""

        return [turn.to_dict() for turn in self.conversation]

    def clear_history(self) -> None:
        """Clear only temporary session conversation history."""

        self.conversation.clear()
        self.updated_at = self.created_at

    def turn_count(self) -> int:
        """Return the number of temporary conversation turns."""

        return len(self.conversation)

    def _context_for_current_turn(
        self,
        current_user_turn: ConversationTurn,
    ) -> PersonaOSContext:
        context = deepcopy(self.persona_os_context)
        metadata = dict(getattr(self.persona_os_context, "metadata", {}) or {})
        metadata["conversation"] = [
            turn.to_dict()
            for turn in self.conversation
            if turn is not current_user_turn
        ]
        metadata["session_id"] = self.id
        if self.memory_retriever is not None:
            retrieved_memory_context = (
                self.memory_retriever.retrieve_relevant_memories(
                    current_user_turn.content,
                    self.persona_os_context,
                )
            )
            context.memories = retrieved_memory_context
            metadata["memory_retrieval"] = {
                "enabled": True,
                "retrieved_count": len(retrieved_memory_context.memories),
                "source": "RuntimeMemoryRetriever",
            }
        setattr(context, "metadata", metadata)
        return context

    def _validate_user_input(self, user_input: str) -> str:
        if not isinstance(user_input, str) or not user_input.strip():
            raise EmptyUserInputError("User input is required.")

        return user_input
