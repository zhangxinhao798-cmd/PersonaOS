"""Tests for in-memory RuntimeSession conversation boundary."""

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
    AssistantResponseError,
    ConversationTurn,
    EmptyUserInputError,
    RuntimeSession,
    RuntimeSessionGenerationError,
)


class FakeChatRuntime:
    def __init__(
        self,
        responses: list[LLMResponse] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.responses = responses or [
            LLMResponse(content="assistant reply", provider="fake")
        ]
        self.error = error
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
        if self.error is not None:
            raise self.error

        response_index = min(len(self.calls) - 1, len(self.responses) - 1)
        return self.responses[response_index]


def make_profile() -> PersonaProfile:
    return PersonaProfile(
        name="Session Architect",
        traits={"focus": "session state"},
        values=["temporary history"],
        style="precise",
        boundaries=["do not create durable memory"],
    )


def make_version() -> PersonaVersion:
    return PersonaVersion(
        id="session-architect-v1",
        persona_name="Session Architect",
        version="1.0",
        created_at="2026-07-16",
        profile_snapshot={"name": "Session Architect"},
        source_ids=["source-1"],
        change_note="Runtime session test version.",
    )


def make_entry() -> PersonaLibraryEntry:
    version = make_version()
    profile = make_profile()
    entry = PersonaLibraryEntry(
        id="session-architect",
        name=profile.name,
        current_version_id=version.id,
        profile=profile,
        versions=[version],
    )
    entry.submit_for_review(reviewer="test")
    entry.approve(reviewer="test")
    entry.activations.append(
        PersonaActivation(
            activation_id="activation-1",
            persona_entry_id=entry.id,
            persona_version_id=version.id,
            status=PersonaActivationStatus.ACTIVE,
        )
    )
    return entry


def make_context() -> PersonaOSContext:
    memory = MemoryRecord(
        content="Session history is not durable memory.",
        category="working",
        confidence=0.8,
        importance=0.7,
        source="test-memory",
        timestamp="2026-07-16T00:00:00Z",
    )
    knowledge = KnowledgeRecord(
        content="RuntimeSession owns temporary conversation only.",
        category="architecture",
        source="test-knowledge",
        confidence=0.9,
        timestamp="2026-07-16T00:00:00Z",
    )
    return PersonaOSContext(
        query="session test",
        persona=PersonaContext(
            name="Session Architect",
            traits=["careful"],
            values=["boundaries"],
            style="precise",
        ),
        memories=MemoryContext(memories=[memory]),
        knowledge=KnowledgeContext(
            knowledge_records=[knowledge],
            sources=[knowledge.source],
        ),
        confidence=ConfidenceContext(score=0.85),
    )


def make_session(
    chat_runtime: FakeChatRuntime | None = None,
) -> tuple[RuntimeSession, PersonaLibraryEntry, PersonaOSContext, FakeChatRuntime]:
    entry = make_entry()
    context = make_context()
    runtime = chat_runtime or FakeChatRuntime()
    session = RuntimeSession(
        id="session-1",
        persona_entry=entry,
        persona_os_context=context,
        chat_runtime=runtime,
    )
    return session, entry, context, runtime


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


def test_conversation_turn_initializes_with_independent_metadata() -> None:
    first = ConversationTurn(role="user")
    second = ConversationTurn(role="assistant")

    first.metadata["trace"] = "first"

    assert first.metadata == {"trace": "first"}
    assert second.metadata == {}


def test_conversation_turn_rejects_unknown_role() -> None:
    with pytest.raises(ValueError):
        ConversationTurn(role="provider")


def test_runtime_session_initializes_with_empty_conversation() -> None:
    session, _, _, _ = make_session()

    assert session.turn_count() == 0
    assert session.get_history() == []


def test_first_successful_send_records_user_and_assistant_turns() -> None:
    session, _, _, _ = make_session()

    session.send("hello")
    history = session.get_history()

    assert [turn["role"] for turn in history] == ["user", "assistant"]
    assert history[0]["content"] == "hello"
    assert history[0]["metadata"]["status"] == "completed"
    assert history[1]["content"] == "assistant reply"


def test_multiple_sends_preserve_turn_ordering() -> None:
    runtime = FakeChatRuntime(
        responses=[
            LLMResponse(content="first reply"),
            LLMResponse(content="second reply"),
        ]
    )
    session, _, _, _ = make_session(runtime)

    session.send("first")
    session.send("second")

    assert [
        (turn["role"], turn["content"])
        for turn in session.get_history()
    ] == [
        ("user", "first"),
        ("assistant", "first reply"),
        ("user", "second"),
        ("assistant", "second reply"),
    ]


def test_prior_conversation_is_passed_into_next_runtime_turn() -> None:
    runtime = FakeChatRuntime(
        responses=[
            LLMResponse(content="first reply"),
            LLMResponse(content="second reply"),
        ]
    )
    session, _, _, _ = make_session(runtime)

    session.send("first")
    session.send("second")

    second_context = runtime.calls[1]["persona_os_context"]
    conversation = second_context.metadata["conversation"]
    assert [
        (turn["role"], turn["content"])
        for turn in conversation
    ] == [
        ("user", "first"),
        ("assistant", "first reply"),
    ]


def test_chat_runtime_is_called_once_per_send() -> None:
    session, _, _, runtime = make_session()

    session.send("one")
    session.send("two")

    assert len(runtime.calls) == 2


def test_llm_response_is_returned_unchanged() -> None:
    response = LLMResponse(content="same response", provider="fake")
    session, _, _, _ = make_session(FakeChatRuntime(responses=[response]))

    result = session.send("hello")

    assert result is response


def test_empty_user_input_is_rejected() -> None:
    session, _, _, runtime = make_session()

    with pytest.raises(EmptyUserInputError):
        session.send("   ")

    assert session.get_history() == []
    assert runtime.calls == []


def test_failed_generation_retains_failed_user_turn_only() -> None:
    session, _, _, runtime = make_session(
        FakeChatRuntime(error=RuntimeError("provider detail"))
    )

    with pytest.raises(RuntimeSessionGenerationError) as exc_info:
        session.send("hello")

    history = session.get_history()
    assert len(runtime.calls) == 1
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "hello"
    assert history[0]["metadata"]["status"] == "failed"
    assert history[0]["metadata"]["error"] == "generation_failed"
    assert str(exc_info.value) == "Runtime session generation failed."


def test_empty_assistant_response_records_failed_user_turn_only() -> None:
    session, _, _, _ = make_session(
        FakeChatRuntime(responses=[LLMResponse(content="")])
    )

    with pytest.raises(AssistantResponseError):
        session.send("hello")

    history = session.get_history()
    assert len(history) == 1
    assert history[0]["metadata"]["status"] == "failed"
    assert history[0]["metadata"]["error"] == "empty_assistant_response"


def test_clear_history_removes_temporary_turns_only() -> None:
    session, entry, _, _ = make_session()
    before = snapshot_entry(entry)
    session.send("hello")

    session.clear_history()

    assert session.get_history() == []
    assert snapshot_entry(entry) == before


def test_get_history_does_not_expose_mutable_internal_state() -> None:
    session, _, _, _ = make_session()
    session.send("hello")
    history = session.get_history()

    history[0]["content"] = "mutated outside"
    history[0]["metadata"]["status"] = "mutated outside"

    fresh_history = session.get_history()
    assert fresh_history[0]["content"] == "hello"
    assert fresh_history[0]["metadata"]["status"] == "completed"


def test_persona_profile_remains_unchanged() -> None:
    session, entry, _, _ = make_session()
    before = copy.deepcopy(entry.profile.__dict__)

    session.send("hello")

    assert entry.profile.__dict__ == before


def test_persona_version_remains_unchanged() -> None:
    session, entry, _, _ = make_session()
    before = copy.deepcopy(entry.versions[0].__dict__)

    session.send("hello")

    assert entry.versions[0].__dict__ == before


def test_persona_library_entry_remains_unchanged() -> None:
    session, entry, _, _ = make_session()
    before = snapshot_entry(entry)

    session.send("hello")

    assert snapshot_entry(entry) == before


def test_existing_memory_and_knowledge_records_remain_unchanged() -> None:
    session, _, context, _ = make_session()
    memory = context.memories.memories[0]
    knowledge = context.knowledge.knowledge_records[0]
    memory_before = copy.deepcopy(memory.__dict__)
    knowledge_before = copy.deepcopy(knowledge.__dict__)

    session.send("hello")

    assert memory.__dict__ == memory_before
    assert knowledge.__dict__ == knowledge_before


def test_unit_tests_use_fake_runtime_without_live_ollama() -> None:
    session, _, _, runtime = make_session()

    session.send("hello")

    assert isinstance(runtime, FakeChatRuntime)
    assert "localhost" not in repr(runtime.calls)

