"""Tests for the minimal PersonaOS interactive CLI."""

import copy
from pathlib import Path

import pytest

from backend.core import PersonaPackageError
from backend.core.knowledge import KnowledgeRecord
from backend.models import (
    LLMResponse,
    PersonaActivation,
    PersonaActivationStatus,
    PersonaLibraryEntry,
    PersonaLibraryLifecycleState,
    PersonaReviewStatus,
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


class FakeAdapter:
    provider = "fake"

    def generate(self, _runtime_context, _user_input: str) -> LLMResponse:
        return LLMResponse(content="fake response")


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


def patch_runtime_dependencies(monkeypatch) -> None:
    monkeypatch.setattr(
        chat_persona,
        "provider_config",
        lambda: ProviderConfig(
            provider="ollama",
            model="qwen3:14b",
            endpoint="http://localhost:11434",
        ),
    )
    monkeypatch.setattr(
        chat_persona,
        "configured_adapter",
        lambda _config: FakeAdapter(),
    )


def test_cli_loads_architect_package_by_default() -> None:
    entry = chat_persona.build_draft_persona_entry()

    assert entry.id == "architect"
    assert entry.name == "Architect"
    assert entry.profile is not None
    assert entry.profile.name == "Architect"


def test_cli_does_not_use_hard_coded_persona_profile() -> None:
    entry = chat_persona.build_draft_persona_entry()

    assert entry.name != "PersonaOS Runtime Guide"
    assert entry.profile is not None
    assert entry.profile.traits["focus"] == "modular architecture"
    assert "review before activation" in entry.profile.values


def test_cli_default_persona_can_be_configured_to_strategist(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)
    monkeypatch.setattr(
        chat_persona,
        "default_persona_package_path",
        lambda: Path("personas") / "strategist",
    )

    runtime = chat_persona.build_runtime()

    assert runtime.persona_entry.id == "strategist"
    assert runtime.persona_entry.name == "Strategist"
    assert runtime.persona_entry.is_selectable() is True


def test_configured_missing_default_persona_has_readable_error(
    capsys,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        chat_persona,
        "default_persona_package_path",
        lambda: Path("personas") / "missing-default",
    )

    result = chat_persona.main()

    assert result == 1
    output = capsys.readouterr().out
    assert "Persona package loading failed:" in output
    assert "missing-default" in output


def test_cli_persona_argument_overrides_configured_default(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)
    captured = {}

    def fake_run_loop(runtime, *_args, **_kwargs) -> int:
        captured["runtime"] = runtime
        return 0

    monkeypatch.setattr(chat_persona, "run_loop", fake_run_loop)

    result = chat_persona.main(["--persona", "strategist"])

    assert result == 0
    runtime = captured["runtime"]
    assert runtime.persona_entry.id == "strategist"
    assert runtime.persona_entry.name == "Strategist"


def test_cli_persona_argument_missing_package_has_readable_error(
    capsys,
    monkeypatch,
) -> None:
    patch_runtime_dependencies(monkeypatch)

    result = chat_persona.main(["--persona", "missing-cli-persona"])

    assert result == 1
    output = capsys.readouterr().out
    assert "Persona package loading failed:" in output
    assert "missing-cli-persona" in output


def test_persona_package_path_from_empty_id_is_rejected() -> None:
    with pytest.raises(PersonaPackageError):
        chat_persona.persona_package_path_from_id("   ")


def test_package_derived_persona_name_appears_in_status(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)
    runtime = chat_persona.build_runtime()
    output: list[str] = []

    chat_persona.handle_command("/status", runtime, output.append)

    assert "Persona: Architect" in output
    assert "Provider: ollama" in output
    assert "Model: qwen3:14b" in output


def test_cli_loads_expression_context_for_default_persona(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)

    runtime = chat_persona.build_runtime()
    expression = runtime.session.persona_os_context.metadata["expression"]

    assert expression["persona_id"] == "architect"
    assert expression["tone"] == "calm, precise, and structured"
    assert "Let's preserve the boundary first." in expression["catchphrases"]
    assert "pause after naming the boundary" in expression["pause_patterns"]


def test_missing_expression_package_keeps_runtime_usable(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)
    entry = chat_persona.prepare_persona_for_cli_runtime(
        Path("personas") / "architect"
    )

    context = chat_persona.build_persona_os_context(
        entry,
        expressions_dir=Path("missing-expressions"),
    )

    assert context.metadata["expression"] == {}


def test_missing_package_path_gives_readable_error(capsys, monkeypatch) -> None:
    def raise_missing_package(_package_path=None) -> None:
        raise PersonaPackageError(
            "Package path does not exist: personas/missing"
        )

    monkeypatch.setattr(chat_persona, "build_runtime", raise_missing_package)

    result = chat_persona.main()

    assert result == 1
    output = capsys.readouterr().out
    assert "Persona package loading failed:" in output
    assert "personas/missing" in output


def test_package_remains_draft_before_cli_startup_approval_flow() -> None:
    entry = chat_persona.build_draft_persona_entry()

    assert entry.lifecycle_state == PersonaLibraryLifecycleState.DRAFT
    assert entry.review_status == PersonaReviewStatus.PENDING_REVIEW
    assert entry.is_approved_for_activation() is False
    assert entry.is_active() is False
    assert entry.is_selectable() is False


def test_cli_startup_approval_flow_is_in_memory(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)

    before = {
        path: path.read_bytes()
        for path in Path("personas/architect").glob("*.json")
    }

    runtime = chat_persona.build_runtime()

    after = {
        path: path.read_bytes()
        for path in Path("personas/architect").glob("*.json")
    }
    assert before == after
    assert runtime.persona_entry.name == "Architect"
    assert runtime.persona_entry.is_approved_for_activation() is True
    assert runtime.persona_entry.is_active() is True
    assert runtime.persona_entry.is_selectable() is True


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
    assert any("/persona info <package_id>" in line for line in output)


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
    assert "Persona package: cli-persona" in output
    assert "Provider: ollama" in output
    assert "Model: qwen3:14b" in output
    assert "Temporary turns: 1" in output


def test_persona_list_displays_available_packages() -> None:
    runtime = make_runtime()
    runtime.personas_dir = Path("personas")
    output: list[str] = []

    chat_persona.handle_command("/persona list", runtime, output.append)

    assert "Available persona packages:" in output
    assert any(
        "architect  Architect  v1.0.0" in line for line in output
    )
    assert any(
        "structured local-first architecture persona" in line
        for line in output
    )


def test_persona_list_displays_second_sample_package() -> None:
    runtime = make_runtime()
    runtime.personas_dir = Path("personas")
    output: list[str] = []

    chat_persona.handle_command("/persona list", runtime, output.append)

    assert any(
        "strategist  Strategist  v1.0.0" in line for line in output
    )
    assert any(
        "decision-focused persona" in line for line in output
    )


def test_persona_info_displays_package_details() -> None:
    runtime = make_runtime()
    runtime.personas_dir = Path("personas")
    output: list[str] = []

    chat_persona.handle_command("/persona info strategist", runtime, output.append)

    assert "Package: strategist" in output
    assert "Name: Strategist" in output
    assert "Version: 1.0.0" in output
    assert any("decision-focused persona" in line for line in output)
    assert "Style: practical, comparative, and concise" in output
    assert "Values:" in output
    assert "  - explicit tradeoffs" in output
    assert "Boundaries:" in output
    assert "  - do not confuse model choice with persona identity" in output
    assert "Examples: 2" in output
    assert "Sources: 2" in output


def test_persona_info_unknown_package_prints_readable_error() -> None:
    runtime = make_runtime()
    runtime.personas_dir = Path("personas")
    output: list[str] = []

    keep_running = chat_persona.handle_command(
        "/persona info missing-package",
        runtime,
        output.append,
    )

    assert keep_running is True
    assert any("Persona package loading failed:" in line for line in output)
    assert any("missing-package" in line for line in output)


def test_persona_use_unknown_package_prints_readable_error() -> None:
    runtime = make_runtime()
    runtime.personas_dir = Path("personas")
    output: list[str] = []

    keep_running = chat_persona.handle_command(
        "/persona use missing-package",
        runtime,
        output.append,
    )

    assert keep_running is True
    assert "Persona package not found: missing-package" in output
    assert runtime.persona_entry.name == "CLI Persona"


def test_persona_use_switches_to_package_persona(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)
    runtime = make_runtime()
    runtime.personas_dir = Path("personas")
    runtime.session.history = [{"role": "user", "content": "old history"}]
    output: list[str] = []

    keep_running = chat_persona.handle_command(
        "/persona use architect",
        runtime,
        output.append,
    )

    assert keep_running is True
    assert "Switched persona to: Architect" in output
    assert runtime.persona_entry.id == "architect"
    assert runtime.persona_entry.name == "Architect"
    assert runtime.persona_entry.is_selectable() is True
    assert runtime.session.turn_count() == 0


def test_persona_use_keeps_package_files_unchanged(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)
    runtime = make_runtime()
    runtime.personas_dir = Path("personas")
    before = {
        path: path.read_bytes()
        for path in Path("personas/architect").glob("*.json")
    }

    chat_persona.handle_command("/persona use architect", runtime, lambda _line: None)

    after = {
        path: path.read_bytes()
        for path in Path("personas/architect").glob("*.json")
    }
    assert before == after


def test_persona_use_switches_expression_context(monkeypatch) -> None:
    patch_runtime_dependencies(monkeypatch)
    runtime = make_runtime()
    runtime.personas_dir = Path("personas")
    runtime.expressions_dir = Path("expressions")

    chat_persona.handle_command("/persona use strategist", runtime, lambda _line: None)

    expression = runtime.session.persona_os_context.metadata["expression"]
    assert runtime.persona_entry.id == "strategist"
    assert expression["persona_id"] == "strategist"
    assert expression["tone"] == "practical, comparative, and direct"
    assert "Let's frame the decision first." in expression["catchphrases"]


def test_persona_command_usage_for_invalid_shape() -> None:
    runtime = make_runtime()
    output: list[str] = []

    chat_persona.handle_command("/persona", runtime, output.append)

    assert "Usage:" in output
    assert "  /persona list" in output
    assert "  /persona info <package_id>" in output
    assert "  /persona use <package_id>" in output


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
