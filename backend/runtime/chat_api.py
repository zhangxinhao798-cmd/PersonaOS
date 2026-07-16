"""Provider-independent chat API boundary for PersonaOS."""

from backend.core.memory_candidate import CandidateExtractor, ReviewQueue
from backend.models.context import PersonaOSContext
from backend.models.llm_response import LLMResponse
from backend.models.persona_library import PersonaLibraryEntry
from backend.runtime.chat_runtime import ChatRuntime
from backend.runtime.memory_runtime import RuntimeMemoryRetriever
from backend.runtime.session_manager import ManagedSession, SessionManager


class ChatApiBoundary:
    """Unified entry point for future Web/API/Frontend chat calls.

    This boundary delegates session lifecycle and generation to SessionManager.
    It does not call providers, adapters, Ollama, or core engines directly.
    """

    def __init__(self, session_manager: SessionManager | None = None) -> None:
        self.session_manager = session_manager or SessionManager()

    def create_session(
        self,
        persona_entry: PersonaLibraryEntry,
        persona_os_context: PersonaOSContext,
        chat_runtime: ChatRuntime,
        session_id: str | None = None,
        metadata: dict | None = None,
        memory_retriever: RuntimeMemoryRetriever | None = None,
        candidate_extractor: CandidateExtractor | None = None,
        review_queue: ReviewQueue | None = None,
    ) -> ManagedSession:
        """Create a temporary chat session."""

        return self.session_manager.create_session(
            persona_entry=persona_entry,
            persona_os_context=persona_os_context,
            chat_runtime=chat_runtime,
            session_id=session_id,
            metadata=metadata,
            memory_retriever=memory_retriever,
            candidate_extractor=candidate_extractor,
            review_queue=review_queue,
        )

    def send_message(self, session_id: str, user_input: str) -> LLMResponse:
        """Send a user message and return the standard LLMResponse."""

        return self.session_manager.send_message(session_id, user_input)

    def get_session(self, session_id: str) -> ManagedSession:
        """Return a managed session."""

        return self.session_manager.get_session(session_id)

    def list_sessions(self) -> list[ManagedSession]:
        """List temporary sessions."""

        return self.session_manager.list_sessions()

    def delete_session(self, session_id: str) -> None:
        """Delete a temporary session."""

        self.session_manager.delete_session(session_id)

    def get_history(self, session_id: str) -> list[dict]:
        """Return detached temporary conversation history."""

        return self.session_manager.get_history(session_id)

    def clear_history(self, session_id: str) -> None:
        """Clear temporary conversation history only."""

        self.session_manager.clear_history(session_id)

    def switch_persona(
        self,
        session_id: str,
        persona_entry: PersonaLibraryEntry,
        persona_os_context: PersonaOSContext,
        chat_runtime: ChatRuntime,
        metadata: dict | None = None,
        memory_retriever: RuntimeMemoryRetriever | None = None,
        candidate_extractor: CandidateExtractor | None = None,
        review_queue: ReviewQueue | None = None,
    ) -> ManagedSession:
        """Switch the active persona reference for a session."""

        return self.session_manager.switch_persona(
            session_id=session_id,
            persona_entry=persona_entry,
            persona_os_context=persona_os_context,
            chat_runtime=chat_runtime,
            metadata=metadata,
            memory_retriever=memory_retriever,
            candidate_extractor=candidate_extractor,
            review_queue=review_queue,
        )
