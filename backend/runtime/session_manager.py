"""Temporary session lifecycle manager for PersonaOS runtime."""

from dataclasses import dataclass, field
from uuid import uuid4

from backend.models.context import PersonaOSContext
from backend.models.llm_response import LLMResponse
from backend.models.persona_library import PersonaLibraryEntry
from backend.runtime.chat_runtime import ChatRuntime
from backend.runtime.session import RuntimeSession


class SessionManagerError(Exception):
    """Base error for temporary session manager failures."""


class DuplicateSessionError(SessionManagerError):
    """Raised when a session id already exists."""


class SessionNotFoundError(SessionManagerError):
    """Raised when a session id cannot be found."""


class InvalidSessionError(SessionManagerError):
    """Raised when required session dependencies are missing."""


@dataclass
class ManagedSession:
    """Managed temporary runtime session state.

    This is not durable memory. It only records the active runtime session,
    current persona reference, and temporary session metadata.
    """

    session_id: str
    runtime_session: RuntimeSession
    active_persona_reference: PersonaLibraryEntry
    persona_os_context: PersonaOSContext
    created_at: str = ""
    updated_at: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.metadata = dict(self.metadata or {})


class SessionManager:
    """Manage temporary PersonaOS runtime sessions.

    SessionManager owns session lifecycle and temporary conversation history
    access. It does not write durable memory, mutate persona records, or own
    provider/runtime generation internals.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ManagedSession] = {}

    def create_session(
        self,
        persona_entry: PersonaLibraryEntry,
        persona_os_context: PersonaOSContext,
        chat_runtime: ChatRuntime,
        session_id: str | None = None,
        metadata: dict | None = None,
    ) -> ManagedSession:
        """Create and register a temporary runtime session."""

        self._validate_session_inputs(persona_entry, persona_os_context, chat_runtime)
        resolved_session_id = session_id or self._new_session_id()
        if resolved_session_id in self._sessions:
            raise DuplicateSessionError(
                f"Session already exists: {resolved_session_id}"
            )

        runtime_session = RuntimeSession(
            id=resolved_session_id,
            persona_entry=persona_entry,
            persona_os_context=persona_os_context,
            chat_runtime=chat_runtime,
            metadata=dict(metadata or {}),
        )
        managed_session = ManagedSession(
            session_id=resolved_session_id,
            runtime_session=runtime_session,
            active_persona_reference=persona_entry,
            persona_os_context=persona_os_context,
            metadata=dict(metadata or {}),
        )
        self._sessions[resolved_session_id] = managed_session
        return managed_session

    def get_session(self, session_id: str) -> ManagedSession:
        """Return a managed session by id."""

        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise SessionNotFoundError(f"Session not found: {session_id}") from exc

    def list_sessions(self) -> list[ManagedSession]:
        """Return managed sessions without exposing the internal registry."""

        return list(self._sessions.values())

    def delete_session(self, session_id: str) -> None:
        """Delete one temporary session."""

        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Session not found: {session_id}")

        del self._sessions[session_id]

    def send_message(self, session_id: str, user_input: str) -> LLMResponse:
        """Send a message through a managed RuntimeSession."""

        return self.get_session(session_id).runtime_session.send(user_input)

    def get_history(self, session_id: str) -> list[dict]:
        """Return detached temporary conversation history for a session."""

        return self.get_session(session_id).runtime_session.get_history()

    def clear_history(self, session_id: str) -> None:
        """Clear temporary conversation history for a session only."""

        managed_session = self.get_session(session_id)
        managed_session.runtime_session.clear_history()
        managed_session.updated_at = managed_session.runtime_session.updated_at

    def switch_persona(
        self,
        session_id: str,
        persona_entry: PersonaLibraryEntry,
        persona_os_context: PersonaOSContext,
        chat_runtime: ChatRuntime,
        metadata: dict | None = None,
    ) -> ManagedSession:
        """Switch the active persona reference for a temporary session.

        v1 uses a fresh RuntimeSession after switching persona so previous
        temporary history cannot be misattributed to the new persona.
        """

        self._validate_session_inputs(persona_entry, persona_os_context, chat_runtime)
        managed_session = self.get_session(session_id)
        merged_metadata = dict(managed_session.metadata)
        if metadata:
            merged_metadata.update(metadata)

        runtime_session = RuntimeSession(
            id=session_id,
            persona_entry=persona_entry,
            persona_os_context=persona_os_context,
            chat_runtime=chat_runtime,
            metadata=merged_metadata,
        )
        managed_session.runtime_session = runtime_session
        managed_session.active_persona_reference = persona_entry
        managed_session.persona_os_context = persona_os_context
        managed_session.metadata = merged_metadata
        managed_session.updated_at = runtime_session.updated_at
        return managed_session

    def session_count(self) -> int:
        """Return the number of active temporary sessions."""

        return len(self._sessions)

    def _validate_session_inputs(
        self,
        persona_entry: PersonaLibraryEntry,
        persona_os_context: PersonaOSContext,
        chat_runtime: ChatRuntime,
    ) -> None:
        if persona_entry is None:
            raise InvalidSessionError("Persona entry is required.")
        if persona_os_context is None:
            raise InvalidSessionError("PersonaOS context is required.")
        if chat_runtime is None:
            raise InvalidSessionError("ChatRuntime is required.")

    def _new_session_id(self) -> str:
        return f"session-{uuid4().hex}"
