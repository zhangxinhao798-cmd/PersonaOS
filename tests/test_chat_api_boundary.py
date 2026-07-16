"""Tests for provider-independent Chat API boundary."""

import copy

from backend.models import LLMResponse
from backend.runtime import ChatApiBoundary, SessionManager

from tests.test_session_manager import (
    FakeChatRuntime,
    make_context,
    make_entry,
    snapshot_entry,
)


def test_chat_api_creates_session_through_session_manager() -> None:
    api = ChatApiBoundary()
    entry = make_entry()
    context = make_context()

    managed = api.create_session(
        entry,
        context,
        FakeChatRuntime(),
        session_id="session-1",
    )

    assert managed.session_id == "session-1"
    assert api.get_session("session-1") is managed


def test_chat_api_request_enters_runtime_and_returns_llm_response() -> None:
    response = LLMResponse(
        content="api reply",
        provider="fake",
        model="fake-model",
    )
    runtime = FakeChatRuntime(response=response)
    api = ChatApiBoundary()
    api.create_session(
        make_entry(),
        make_context(),
        runtime,
        session_id="session-1",
    )

    result = api.send_message("session-1", "hello from api")

    assert result is response
    assert len(runtime.calls) == 1
    assert runtime.calls[0]["user_input"] == "hello from api"


def test_chat_api_does_not_call_provider_or_adapter_directly() -> None:
    runtime = FakeChatRuntime()
    api = ChatApiBoundary()
    api.create_session(
        make_entry(),
        make_context(),
        runtime,
        session_id="session-1",
    )

    api.send_message("session-1", "hello")

    assert len(runtime.calls) == 1
    assert "localhost" not in repr(runtime.calls)
    assert "ollama" not in repr(runtime.calls).lower()


def test_chat_api_history_and_clear_are_session_scoped() -> None:
    api = ChatApiBoundary()
    api.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(response=LLMResponse(content="first reply")),
        session_id="session-1",
    )
    api.create_session(
        make_entry("Second Persona"),
        make_context("Second Persona"),
        FakeChatRuntime(response=LLMResponse(content="second reply")),
        session_id="session-2",
    )

    api.send_message("session-1", "first")
    api.send_message("session-2", "second")
    api.clear_history("session-1")

    assert api.get_history("session-1") == []
    assert api.get_history("session-2")[1]["content"] == "second reply"


def test_chat_api_lists_and_deletes_sessions() -> None:
    api = ChatApiBoundary()
    api.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(),
        session_id="session-1",
    )

    assert [session.session_id for session in api.list_sessions()] == ["session-1"]

    api.delete_session("session-1")

    assert api.list_sessions() == []


def test_chat_api_switch_persona_uses_session_manager() -> None:
    api = ChatApiBoundary()
    api.create_session(
        make_entry(),
        make_context(),
        FakeChatRuntime(),
        session_id="session-1",
    )
    api.send_message("session-1", "before switch")
    second_entry = make_entry("Second Persona")

    switched = api.switch_persona(
        "session-1",
        second_entry,
        make_context("Second Persona"),
        FakeChatRuntime(response=LLMResponse(content="second reply")),
    )

    assert switched.active_persona_reference is second_entry
    assert api.get_history("session-1") == []


def test_chat_api_does_not_mutate_durable_persona_state() -> None:
    entry = make_entry()
    context = make_context()
    before = snapshot_entry(entry)
    memory = context.memories.memories[0]
    knowledge = context.knowledge.knowledge_records[0]
    memory_before = copy.deepcopy(memory.__dict__)
    knowledge_before = copy.deepcopy(knowledge.__dict__)
    api = ChatApiBoundary(SessionManager())
    api.create_session(entry, context, FakeChatRuntime(), session_id="session-1")

    api.send_message("session-1", "hello")

    assert snapshot_entry(entry) == before
    assert memory.__dict__ == memory_before
    assert knowledge.__dict__ == knowledge_before
