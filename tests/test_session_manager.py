"""Tests for temporary SessionManager lifecycle boundary."""

import copy

import pytest

from backend.core.knowledge import KnowledgeRecord
from backend.models import (
    LLMResponse,
    PersonaActivation,
    PersonaActivationStatus,
    PersonaLibraryEntry,
    PersonaProfile,
    PersonaVersion,
    RelationshipContext,
)
from backend.models.context import (
    ConfidenceContext,
    KnowledgeContext,
    MemoryContext,
    PersonaContext,
    PersonaOSContext,
)
from backend.models.memory_record import MemoryRecord
from backend.runtime import (
    DuplicateSessionError,
    InvalidSessionError,
    ManagedSession,
    SessionManager,
    SessionNotFoundError,
)


class FakeChatRuntime:
    def __init__(self, response: LLMResponse | None = None) -> None:
        self.response = response or LLMResponse(
            content="managed reply",
            provider="fake",
            model="fake-model",
        )
        self.calls: list[dict] = []

    def generate_reply(
        self,
        user_input: str,
        persona_entry: PersonaLibraryEntry,
        persona_os_context: PersonaOSContext,
    ) -> LLMResponse:
        self.calls.append(
            {
                "user_input": user_input,
                "persona_entry": persona_entry,
                "persona_os_context": persona_os_context,
            }
        )
        return self.response


class TrackingSessionRepository:
    def __init__(self) -> None:
        self.sessions: dict[str, ManagedSession] = {}
        self.calls: list[tuple[str, str | None]] = []

    def exists(self, session_id: str) -> bool:
        self.calls.append(("exists", session_id))
        return session_id in self.sessions

    def save(self, session: ManagedSession) -> None:
        self.calls.append(("save", session.session_id))
        self.sessions[session.session_id] = session

    def get(self, session_id: str) -> ManagedSession | None:
        self.calls.append(("get", session_id))
        return self.sessions.get(session_id)

    def list(self) -> list[ManagedSession]:
        self.calls.append(("list", None))
        return list(self.sessions.values())

    def delete(self, session_id: str) -> bool:
        self.calls.append(("delete", session_id))
        if session_id not in self.sessions:
            return False

        del self.sessions[session_id]
        return True

    def count(self) -> int:
        self.calls.append(("count", None))
        return len(self.sessions)


def make_profile(name: str = "Session Architect") -> PersonaProfile:
    return PersonaProfile(
        name=name,
        traits={"focus": "temporary sessions"},
        values=["clear boundaries"],
        style="precise",
        boundaries=["do not write durable memory"],
    )


def make_version(name: str = "Session Architect") -> PersonaVersion:
    return PersonaVersion(
        id=f"{name.lower().replace(' ', '-')}-v1",
        persona_name=name,
        version="1.0",
        created_at="2026-07-16",
        profile_snapshot={"name": name},
        source_ids=["source-1"],
        change_note="Session manager test version.",
    )


def make_entry(name: str = "Session Architect") -> PersonaLibraryEntry:
    profile = make_profile(name)
    version = make_version(name)
    entry = PersonaLibraryEntry(
        id=name.lower().replace(" ", "-"),
        name=name,
        current_version_id=version.id,
        profile=profile,
        versions=[version],
    )
    entry.submit_for_review(reviewer="test")
    entry.approve(reviewer="test")
    entry.activations.append(
        PersonaActivation(
            activation_id=f"{entry.id}-activation",
            persona_entry_id=entry.id,
            persona_version_id=version.id,
            status=PersonaActivationStatus.ACTIVE,
        )
    )
    return entry


def make_context(name: str = "Session Architect") -> PersonaOSContext:
    memory = MemoryRecord(
        content=f"{name} temporary session memory fixture.",
        category="working",
        confidence=0.8,
        importance=0.7,
        source="test-memory",
        timestamp="2026-07-16T00:00:00Z",
    )
    knowledge = KnowledgeRecord(
        content="SessionManager does not connect to MemoryEngine.",
        category="architecture",
        source="test-knowledge",
        confidence=0.9,
        timestamp="2026-07-16T00:00:00Z",
    )
    return PersonaOSContext(
        query="session manager test",
        persona=PersonaContext(
            name=name,
            traits=["careful"],
            values=["separation"],
            style="precise",
        ),
        memories=MemoryContext(memories=[memory]),
        knowledge=KnowledgeContext(
            knowledge_records=[knowledge],
            sources=[knowledge.source],
        ),
        confidence=ConfidenceContext(score=0.85),
    )


def make_relationship() -> RelationshipContext:
    return RelationshipContext(
        relationship_type="companion",
        interaction_style="warm",
        tone="supportive",
        permissions=["chat"],
        metadata={"user_id": "session-user"},
    )


def snapshot_entry(entry: PersonaLibraryEntry) -> dict:
    return {
        "profile": copy.deepcopy(entry.profile.__dict__),
        "versions": copy.deepcopy([version.__dict__ for version in entry.versions]),
        "entry": {
            "id": entry.id,
            "name": entry.name,
            "lifecycle_state": entry.lifecycle_state,
            "review_status": entry.review_status,
            "current_version_id": entry.current_version_id,
        },
        "reviews": copy.deepcopy([review.__dict__ for review in entry.reviews]),
        "activations": copy.deepcopy(
            [activation.__dict__ for activation in entry.activations]
        ),
    }


def test_create_session_registers_runtime_session() -> None:
    manager = SessionManager()
    entry = make_entry()
    context = make_context()
    runtime = FakeChatRuntime()

    managed = manager.create_session(
        entry,
        context,
        runtime,
        session_id="session-1",
        metadata={"source": "test"},
    )

    assert managed.session_id == "session-1"
    assert managed.runtime_session.id == "session-1"
    assert managed.active_persona_reference is entry
    assert managed.persona_os_context is context
    assert managed.metadata == {"source": "test"}
    assert manager.session_count() == 1


def test_create_session_can_carry_relationship_reference() -> None:
    manager = SessionManager()
    relationship = make_relationship()

    managed = manager.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(),
        session_id="session-relationship",
        relationship_context=relationship,
    )

    assert managed.active_relationship_reference is relationship
    assert managed.runtime_session.relationship_context is relationship
    assert not hasattr(managed.active_persona_reference.profile, "relationship_type")


def test_session_manager_uses_repository_boundary() -> None:
    repository = TrackingSessionRepository()
    manager = SessionManager(repository=repository)

    managed = manager.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(),
        session_id="session-1",
    )
    fetched = manager.get_session("session-1")
    listed = manager.list_sessions()
    count = manager.session_count()
    manager.delete_session("session-1")

    assert fetched is managed
    assert listed == [managed]
    assert count == 1
    assert repository.calls == [
        ("exists", "session-1"),
        ("save", "session-1"),
        ("get", "session-1"),
        ("list", None),
        ("count", None),
        ("delete", "session-1"),
    ]


def test_create_session_generates_id_when_missing() -> None:
    manager = SessionManager()

    managed = manager.create_session(make_entry(), make_context(), FakeChatRuntime())

    assert managed.session_id.startswith("session-")
    assert manager.get_session(managed.session_id) is managed


def test_duplicate_session_id_is_rejected() -> None:
    manager = SessionManager()
    manager.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(),
        session_id="session-1",
    )

    with pytest.raises(DuplicateSessionError):
        manager.create_session(
            make_entry("Second Persona"),
            make_context("Second Persona"),
            FakeChatRuntime(),
            session_id="session-1",
        )


def test_get_missing_session_is_rejected() -> None:
    manager = SessionManager()

    with pytest.raises(SessionNotFoundError):
        manager.get_session("missing")


def test_invalid_session_dependencies_are_rejected() -> None:
    manager = SessionManager()

    with pytest.raises(InvalidSessionError):
        manager.create_session(None, make_context(), FakeChatRuntime())  # type: ignore[arg-type]
    with pytest.raises(InvalidSessionError):
        manager.create_session(make_entry(), None, FakeChatRuntime())  # type: ignore[arg-type]
    with pytest.raises(InvalidSessionError):
        manager.create_session(make_entry(), make_context(), None)  # type: ignore[arg-type]


def test_list_sessions_returns_registered_sessions() -> None:
    manager = SessionManager()
    first = manager.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(),
        session_id="session-1",
    )
    second = manager.create_session(
        make_entry("Second Persona"),
        make_context("Second Persona"),
        FakeChatRuntime(),
        session_id="session-2",
    )

    assert manager.list_sessions() == [first, second]


def test_delete_session_removes_temporary_session() -> None:
    manager = SessionManager()
    manager.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(),
        session_id="session-1",
    )

    manager.delete_session("session-1")

    assert manager.list_sessions() == []
    with pytest.raises(SessionNotFoundError):
        manager.get_session("session-1")


def test_send_message_records_temporary_history() -> None:
    manager = SessionManager()
    runtime = FakeChatRuntime()
    manager.create_session(
        make_entry(),
        make_context(),
        runtime,
        session_id="session-1",
    )

    response = manager.send_message("session-1", "hello")
    history = manager.get_history("session-1")

    assert response is runtime.response
    assert [turn["role"] for turn in history] == ["user", "assistant"]
    assert history[0]["content"] == "hello"
    assert history[1]["content"] == "managed reply"


def test_clear_history_only_clears_temporary_conversation() -> None:
    manager = SessionManager()
    entry = make_entry()
    before = snapshot_entry(entry)
    manager.create_session(
        entry,
        make_context(),
        FakeChatRuntime(),
        session_id="session-1",
    )
    manager.send_message("session-1", "hello")

    manager.clear_history("session-1")

    assert manager.get_history("session-1") == []
    assert snapshot_entry(entry) == before


def test_switch_persona_updates_reference_and_resets_history() -> None:
    manager = SessionManager()
    first_entry = make_entry()
    second_entry = make_entry("Second Persona")
    manager.create_session(
        first_entry,
        make_context(),
        FakeChatRuntime(),
        session_id="session-1",
    )
    manager.send_message("session-1", "before switch")

    switched = manager.switch_persona(
        "session-1",
        second_entry,
        make_context("Second Persona"),
        FakeChatRuntime(response=LLMResponse(content="second reply")),
        metadata={"reason": "user requested"},
    )

    assert switched.session_id == "session-1"
    assert switched.active_persona_reference is second_entry
    assert switched.runtime_session.persona_entry is second_entry
    assert switched.runtime_session.get_history() == []
    assert switched.metadata["reason"] == "user requested"


def test_sessions_are_isolated() -> None:
    manager = SessionManager()
    manager.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(response=LLMResponse(content="first reply")),
        session_id="session-1",
    )
    manager.create_session(
        make_entry("Second Persona"),
        make_context("Second Persona"),
        FakeChatRuntime(response=LLMResponse(content="second reply")),
        session_id="session-2",
    )

    manager.send_message("session-1", "first")
    manager.send_message("session-2", "second")

    assert manager.get_history("session-1")[1]["content"] == "first reply"
    assert manager.get_history("session-2")[1]["content"] == "second reply"


def test_manager_does_not_mutate_persona_memory_or_knowledge_records() -> None:
    manager = SessionManager()
    entry = make_entry()
    context = make_context()
    entry_before = snapshot_entry(entry)
    memory = context.memories.memories[0]
    knowledge = context.knowledge.knowledge_records[0]
    memory_before = copy.deepcopy(memory.__dict__)
    knowledge_before = copy.deepcopy(knowledge.__dict__)
    manager.create_session(entry, context, FakeChatRuntime(), session_id="session-1")

    manager.send_message("session-1", "hello")

    assert snapshot_entry(entry) == entry_before
    assert memory.__dict__ == memory_before
    assert knowledge.__dict__ == knowledge_before
