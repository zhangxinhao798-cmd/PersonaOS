"""Session repository boundary for PersonaOS runtime sessions."""

from dataclasses import dataclass, field
from typing import Protocol

from backend.models.context import PersonaOSContext
from backend.models.persona_library import PersonaLibraryEntry
from backend.runtime.session import RuntimeSession


@dataclass
class ManagedSession:
    """Managed temporary runtime session state.

    This is not durable memory. It records the active runtime session,
    current persona reference, prepared context, and session metadata.
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


class SessionRepository(Protocol):
    """Storage boundary for managed runtime sessions."""

    def exists(self, session_id: str) -> bool:
        """Return whether a session exists."""

    def save(self, session: ManagedSession) -> None:
        """Create or replace a managed session."""

    def get(self, session_id: str) -> ManagedSession | None:
        """Return a managed session or None."""

    def list(self) -> list[ManagedSession]:
        """Return managed sessions."""

    def delete(self, session_id: str) -> bool:
        """Delete a managed session and return whether one was removed."""

    def count(self) -> int:
        """Return the number of sessions."""


class InMemorySessionRepository:
    """In-memory SessionRepository implementation.

    This is the current v1 repository. It does not persist across process
    restarts and does not write to files or databases.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ManagedSession] = {}

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def save(self, session: ManagedSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> ManagedSession | None:
        return self._sessions.get(session_id)

    def list(self) -> list[ManagedSession]:
        return list(self._sessions.values())

    def delete(self, session_id: str) -> bool:
        if session_id not in self._sessions:
            return False

        del self._sessions[session_id]
        return True

    def count(self) -> int:
        return len(self._sessions)
