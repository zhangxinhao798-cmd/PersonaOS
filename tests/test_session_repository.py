"""Tests for SessionRepository boundary."""

from backend.runtime import InMemorySessionRepository

from tests.test_session_manager import FakeChatRuntime, make_context, make_entry
from backend.runtime import ManagedSession, RuntimeSession


def make_managed_session(session_id: str = "session-1") -> ManagedSession:
    entry = make_entry()
    context = make_context()
    runtime_session = RuntimeSession(
        id=session_id,
        persona_entry=entry,
        persona_os_context=context,
        chat_runtime=FakeChatRuntime(),
    )
    return ManagedSession(
        session_id=session_id,
        runtime_session=runtime_session,
        active_persona_reference=entry,
        persona_os_context=context,
        metadata={"source": "test"},
    )


def test_in_memory_repository_starts_empty() -> None:
    repository = InMemorySessionRepository()

    assert repository.count() == 0
    assert repository.list() == []
    assert not repository.exists("missing")
    assert repository.get("missing") is None


def test_in_memory_repository_saves_and_gets_session() -> None:
    repository = InMemorySessionRepository()
    session = make_managed_session()

    repository.save(session)

    assert repository.exists("session-1")
    assert repository.get("session-1") is session
    assert repository.list() == [session]
    assert repository.count() == 1


def test_in_memory_repository_replaces_existing_session() -> None:
    repository = InMemorySessionRepository()
    first = make_managed_session("session-1")
    second = make_managed_session("session-1")
    second.metadata["replacement"] = True

    repository.save(first)
    repository.save(second)

    assert repository.get("session-1") is second
    assert repository.count() == 1
    assert repository.get("session-1").metadata["replacement"] is True


def test_in_memory_repository_deletes_session() -> None:
    repository = InMemorySessionRepository()
    session = make_managed_session()
    repository.save(session)

    removed = repository.delete("session-1")
    missing = repository.delete("session-1")

    assert removed is True
    assert missing is False
    assert repository.get("session-1") is None
    assert repository.count() == 0
