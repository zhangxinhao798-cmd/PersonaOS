"""Tests for the minimal PersonaOS interactive CLI."""

import copy

from backend.core.knowledge import KnowledgeRecord
from backend.models import (
    LLMResponse,
    PersonaActivation,
    PersonaActivationStatus,
    PersonaLibraryEntry,
    PersonaProfile,
    PersonaVersion,
    ProviderConfig,
)
from backend.models.memory_record import MemoryRecord
from scripts import chat_persona


class FakeSession:
    def __init__(
        self,
        response: LLMResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response or LLMResponse(content="assistant says hello")
        self.error = error
        self.sent: list[str] = []
        self.history: list[dict] = []
        self.clear_calls = 0

    def send(self, user_input: str) -> LLMResponse:
        self.sent.append(user_input)
        if self.error is not None:
            raise self.error

        self.history.extend(
            [
                {"role": "user", "content": user_input, "metadata": {}},
                {
                    "role": "assistant",
                    "content": self.response.content,
                    "metadata": {},
                },
            ]
        )
        return self.response

    def get_history(self) -> list[dict]:
        return copy.deepcopy(self.history)

    def clear_history(self) -> None:
        self.clear_calls += 1
        self.history.clear()

    def turn_count(self) -> int:
        return len(self.history)


def make_entry() -> PersonaLibraryEntry:
    profile = PersonaProfile(
        name="CLI Persona",
        traits={"focus": "testing"},
        values=["boundaries"],
        style="concise",
        boundaries=["no durable writes"],
    )
    version = PersonaVersion(
        id="cli-persona-v1",
        persona_name=profile.name,
        version="1.0",
        profile_snapshot={"name": profile.name},
    )
    entry = PersonaLibraryEntry(
        id="cli-persona",
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


def make_runtime(
    session: FakeSession | None = None,
) -> chat_persona.InteractiveRuntime:
    return chat_persona.InteractiveRuntime(
        session=session or FakeSession(),
        persona_entry=make_entry(),
        provider_config=ProviderConfig(
            provider="ollama",
            model="qwen3:14b",
            endpoint="http://localhost:11434",
        ),
    )


def test_help_does_not_call_runtime_session_send() -> None:
    session = FakeSession()
    output: list[str] = []

    keep_running = chat_persona.handle_command(
        "/help",
        make_runtime(session),
        output.append,
    )

    assert keep_running is True
    assert session.sent == []
    assert any("/history" in line for line in output)


def test_exit_ends_loop() -> None:
    session = FakeSession()
    inputs = iter(["/exit"])
    output: list[str] = []

    result = chat_persona.run_loop(
        make_runtime(session),
        input_reader=lambda _prompt: next(inputs),
        printer=output.append,
    )

    assert result == 0
    assert session.sent == []
    assert "Session ended." in output


def test_history_displays_temporary_turns() -> None:
    session = FakeSession()
    session.history = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    output: list[str] = []

    chat_persona.handle_command("/history", make_runtime(session), output.append)

    assert "1. user: hello" in output
    assert "2. assistant: hi" in output


def test_clear_clears_session_history() -> None:
    session = FakeSession()
    session.history = [{"role": "user", "content": "hello"}]
    output: list[str] = []

    chat_persona.handle_command("/clear", make_runtime(session), output.append)

    assert session.history == []
    assert session.clear_calls == 1
    assert "Temporary history cleared." in output


def test_status_displays_persona_provider_model_and_turn_count() -> None:
    session = FakeSession()
    session.history = [{"role": "user", "content": "hello"}]
    output: list[str] = []

    chat_persona.handle_command("/status", make_runtime(session), output.append)

    assert "Persona: CLI Persona" in output
    assert "Provider: ollama" in output
    assert "Model: qwen3:14b" in output
    assert "Temporary turns: 1" in output


def test_normal_input_calls_runtime_session_send_once() -> None:
    session = FakeSession()
    inputs = iter(["hello", "/exit"])

    chat_persona.run_loop(
        make_runtime(session),
        input_reader=lambda _prompt: next(inputs),
        printer=lambda _line: None,
    )

    assert session.sent == ["hello"]


def test_assistant_content_is_printed() -> None:
    session = FakeSession(response=LLMResponse(content="你好，我是 PersonaOS。"))
    inputs = iter(["你好", "/exit"])
    output: list[str] = []

    chat_persona.run_loop(
        make_runtime(session),
        input_reader=lambda _prompt: next(inputs),
        printer=output.append,
    )

    assert "你好，我是 PersonaOS。" in output


def test_empty_input_is_ignored() -> None:
    session = FakeSession()
    inputs = iter(["", "   ", "/exit"])

    chat_persona.run_loop(
        make_runtime(session),
        input_reader=lambda _prompt: next(inputs),
        printer=lambda _line: None,
    )

    assert session.sent == []


def test_runtime_errors_produce_readable_message() -> None:
    session = FakeSession(
        error=chat_persona.RuntimeSessionGenerationError(
            "Runtime session generation failed."
        )
    )
    inputs = iter(["hello", "/exit"])
    output: list[str] = []

    chat_persona.run_loop(
        make_runtime(session),
        input_reader=lambda _prompt: next(inputs),
        printer=output.append,
    )

    assert "Runtime generation failed. No durable state was written." in output


def test_ctrl_c_exits_cleanly() -> None:
    output: list[str] = []

    def raise_keyboard_interrupt(_prompt: str) -> str:
        raise KeyboardInterrupt

    result = chat_persona.run_loop(
        make_runtime(),
        input_reader=raise_keyboard_interrupt,
        printer=output.append,
    )

    assert result == 0
    assert "Session interrupted. Goodbye." in output


def test_no_durable_persona_or_memory_state_is_mutated() -> None:
    runtime = make_runtime()
    entry_before = {
        "profile": copy.deepcopy(runtime.persona_entry.profile.__dict__),
        "version": copy.deepcopy(runtime.persona_entry.versions[0].__dict__),
        "entry": {
            "current_version_id": runtime.persona_entry.current_version_id,
            "review_status": runtime.persona_entry.review_status,
            "lifecycle_state": runtime.persona_entry.lifecycle_state,
        },
    }
    memory = MemoryRecord(
        content="temporary cli memory",
        category="working",
        confidence=0.8,
        importance=0.7,
        source="test",
        timestamp="now",
    )
    knowledge = KnowledgeRecord(
        content="temporary cli knowledge",
        category="architecture",
        source="test",
        confidence=0.9,
        timestamp="now",
    )
    memory_before = copy.deepcopy(memory.__dict__)
    knowledge_before = copy.deepcopy(knowledge.__dict__)
    inputs = iter(["hello", "/history", "/clear", "/exit"])

    chat_persona.run_loop(
        runtime,
        input_reader=lambda _prompt: next(inputs),
        printer=lambda _line: None,
    )

    assert runtime.persona_entry.profile.__dict__ == entry_before["profile"]
    assert runtime.persona_entry.versions[0].__dict__ == entry_before["version"]
    assert runtime.persona_entry.current_version_id == (
        entry_before["entry"]["current_version_id"]
    )
    assert runtime.persona_entry.review_status == (
        entry_before["entry"]["review_status"]
    )
    assert runtime.persona_entry.lifecycle_state == (
        entry_before["entry"]["lifecycle_state"]
    )
    assert memory.__dict__ == memory_before
    assert knowledge.__dict__ == knowledge_before

