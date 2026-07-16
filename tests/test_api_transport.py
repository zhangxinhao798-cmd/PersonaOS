"""Tests for dependency-free API Transport Layer v1."""

import copy
import inspect
import json

from backend.api import ApiTransport, PersonaRuntimeBundle
from backend.api import transport as api_transport_module
from backend.models import LLMResponse
from backend.runtime import RuntimeMemoryRetriever
from backend.runtime import ChatApiBoundary

from tests.test_session_manager import (
    FakeChatRuntime,
    make_context,
    make_entry,
    snapshot_entry,
)


class FakeRuntimeProvider:
    def __init__(self) -> None:
        self.entry = make_entry()
        self.context = make_context()
        self.runtime = FakeChatRuntime(
            response=LLMResponse(
                content="api transport reply",
                provider="fake",
                model="fake-model",
                usage={"tokens": 3},
            )
        )
        self.bundle_calls: list[str | None] = []

    def list_personas(self) -> list[dict]:
        return [
            {
                "id": self.entry.id,
                "name": self.entry.name,
                "current_version_id": self.entry.current_version_id,
            }
        ]

    def get_runtime_bundle(
        self,
        persona_id: str | None = None,
    ) -> PersonaRuntimeBundle:
        self.bundle_calls.append(persona_id)
        return PersonaRuntimeBundle(
            persona_id=self.entry.id,
            name=self.entry.name,
            persona_entry=self.entry,
            persona_os_context=self.context,
            chat_runtime=self.runtime,
            metadata={"source": "fake-provider"},
        )


def make_transport() -> tuple[ApiTransport, FakeRuntimeProvider]:
    provider = FakeRuntimeProvider()
    transport = ApiTransport(
        chat_api=ChatApiBoundary(),
        runtime_provider=provider,
    )
    return transport, provider


def test_get_personas_returns_available_personas() -> None:
    transport, provider = make_transport()

    response = transport.handle_request("GET", "/personas")

    assert response.status_code == 200
    assert response.body["personas"] == provider.list_personas()


def test_create_session_success() -> None:
    transport, provider = make_transport()

    response = transport.handle_request(
        "POST",
        "/sessions",
        {"session_id": "session-1", "persona_id": "session-architect"},
    )

    assert response.status_code == 201
    session = response.body["session"]
    assert session["session_id"] == "session-1"
    assert session["active_persona"]["id"] == provider.entry.id
    assert session["metadata"]["persona_id"] == provider.entry.id
    assert provider.bundle_calls == ["session-architect"]


def test_get_session_success() -> None:
    transport, _ = make_transport()
    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})

    response = transport.handle_request("GET", "/sessions/session-1")

    assert response.status_code == 200
    assert response.body["session"]["session_id"] == "session-1"
    assert response.body["session"]["turn_count"] == 0


def test_list_sessions_success() -> None:
    transport, _ = make_transport()
    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})
    transport.handle_request("POST", "/sessions", {"session_id": "session-2"})

    response = transport.handle_request("GET", "/sessions")

    assert response.status_code == 200
    assert [session["session_id"] for session in response.body["sessions"]] == [
        "session-1",
        "session-2",
    ]


def test_get_session_history_success() -> None:
    transport, _ = make_transport()
    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})
    transport.handle_request(
        "POST",
        "/sessions/session-1/messages",
        {"message": "hello history"},
    )

    response = transport.handle_request("GET", "/sessions/session-1/history")

    assert response.status_code == 200
    assert response.body["session_id"] == "session-1"
    assert response.body["history"] == [
        {
            "role": "user",
            "content": "hello history",
            "created_at": "",
            "metadata": {"status": "completed"},
        },
        {
            "role": "assistant",
            "content": "api transport reply",
            "created_at": "",
            "metadata": {
                "status": "completed",
                "provider": "fake",
                "model": "fake-model",
            },
        },
    ]


def test_delete_session_success() -> None:
    transport, _ = make_transport()
    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})

    response = transport.handle_request("DELETE", "/sessions/session-1")

    assert response.status_code == 200
    assert response.body == {"deleted": True, "session_id": "session-1"}
    missing = transport.handle_request("GET", "/sessions/session-1")
    assert missing.status_code == 404


def test_send_message_success_returns_standard_response() -> None:
    transport, provider = make_transport()
    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})

    response = transport.handle_request(
        "POST",
        "/sessions/session-1/messages",
        {"message": "hello api"},
    )

    assert response.status_code == 200
    assert response.body == {
        "session_id": "session-1",
        "persona": {
            "id": provider.entry.id,
            "name": provider.entry.name,
            "version": provider.entry.current_version_id,
        },
        "message": {
            "role": "assistant",
            "content": "api transport reply",
        },
        "model": {
            "provider": "fake",
            "name": "fake-model",
        },
        "metadata": {},
        "usage": {"tokens": 3},
    }
    assert provider.runtime.calls[0]["user_input"] == "hello api"


def test_send_message_accepts_user_input_alias() -> None:
    transport, provider = make_transport()
    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})

    response = transport.handle_request(
        "POST",
        "/sessions/session-1/messages",
        {"user_input": "hello alias"},
    )

    assert response.status_code == 200
    assert provider.runtime.calls[0]["user_input"] == "hello alias"


def test_message_response_schema_is_json_serializable() -> None:
    transport, _ = make_transport()
    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})

    response = transport.handle_request(
        "POST",
        "/sessions/session-1/messages",
        {"message": "hello json"},
    )

    encoded = json.dumps(response.body)
    decoded = json.loads(encoded)
    assert decoded["message"]["role"] == "assistant"
    assert decoded["message"]["content"] == "api transport reply"
    assert decoded["persona"]["id"]
    assert decoded["model"]["provider"] == "fake"


def test_error_input_handling() -> None:
    transport, _ = make_transport()

    missing_route = transport.handle_request("GET", "/missing")
    invalid_session_id = transport.handle_request(
        "POST",
        "/sessions",
        {"session_id": 123},
    )
    missing_message = transport.handle_request(
        "POST",
        "/sessions/session-1/messages",
        {"message": "  "},
    )

    assert missing_route.status_code == 404
    assert invalid_session_id.status_code == 400
    assert missing_message.status_code == 400


def test_api_does_not_modify_persona_or_memory_state() -> None:
    transport, provider = make_transport()
    entry_before = snapshot_entry(provider.entry)
    memory = provider.context.memories.memories[0]
    knowledge = provider.context.knowledge.knowledge_records[0]
    memory_before = copy.deepcopy(memory.__dict__)
    knowledge_before = copy.deepcopy(knowledge.__dict__)

    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})
    transport.handle_request(
        "POST",
        "/sessions/session-1/messages",
        {"message": "hello"},
    )

    assert snapshot_entry(provider.entry) == entry_before
    assert memory.__dict__ == memory_before
    assert knowledge.__dict__ == knowledge_before


def test_api_session_can_inject_runtime_memory_retrieval() -> None:
    provider = FakeRuntimeProvider()
    transport = ApiTransport(
        chat_api=ChatApiBoundary(),
        runtime_provider=provider,
    )

    original_get_runtime_bundle = provider.get_runtime_bundle

    def get_runtime_bundle_with_memory(persona_id: str | None = None):
        bundle = original_get_runtime_bundle(persona_id)
        bundle.memory_retriever = RuntimeMemoryRetriever()
        return bundle

    provider.get_runtime_bundle = get_runtime_bundle_with_memory

    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})
    response = transport.handle_request(
        "POST",
        "/sessions/session-1/messages",
        {"message": "temporary session memory fixture"},
    )

    runtime_context = provider.runtime.calls[0]["persona_os_context"]
    assert response.status_code == 200
    assert len(runtime_context.memories.memories) == 1
    assert (
        runtime_context.memories.memories[0].content
        == "Session Architect temporary session memory fixture."
    )
    assert runtime_context.memories.relevance[0]["rank"] == 1
    assert runtime_context.metadata["memory_retrieval"]["enabled"] is True


def test_api_does_not_bypass_chat_runtime() -> None:
    transport, provider = make_transport()
    transport.handle_request("POST", "/sessions", {"session_id": "session-1"})

    transport.handle_request(
        "POST",
        "/sessions/session-1/messages",
        {"message": "runtime path"},
    )

    assert len(provider.runtime.calls) == 1
    assert provider.runtime.calls[0]["user_input"] == "runtime path"


def test_api_transport_does_not_directly_call_provider_or_ollama() -> None:
    source = inspect.getsource(api_transport_module)

    assert "OllamaAdapter" not in source
    assert "ollama" not in source.lower()
    assert ".generate(" not in source
    assert "BaseLLMAdapter" not in source


def test_api_transport_does_not_import_memory_engine() -> None:
    source = inspect.getsource(api_transport_module)

    assert "MemoryEngine" not in source
    assert "backend.core.memory" not in source
