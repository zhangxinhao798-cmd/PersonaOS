"""Minimal local PersonaOS interactive runtime CLI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.adapters import (  # noqa: E402
    OllamaResponseError,
    OllamaTransportError,
)
from backend.core import (  # noqa: E402
    PersonaActivationManager,
    PersonaLibraryEngine,
    PersonaSelector,
)
from backend.core.knowledge import KnowledgeRecord  # noqa: E402
from backend.engine.runtime_context_assembler import (  # noqa: E402
    RuntimeContextAssembler,
)
from backend.models import (  # noqa: E402
    PersonaLibraryEntry,
    PersonaProfile,
    PersonaVersion,
    ProviderConfig,
)
from backend.models.context import (  # noqa: E402
    ConfidenceContext,
    KnowledgeContext,
    MemoryContext,
    PersonaContext,
    PersonaOSContext,
)
from backend.models.memory_record import MemoryRecord  # noqa: E402
from backend.runtime import (  # noqa: E402
    AdapterGenerationError,
    AssistantResponseError,
    ChatRuntime,
    ChatRuntimeError,
    EmptyUserInputError,
    RuntimeSession,
    RuntimeSessionGenerationError,
)
from config.runtime import (  # noqa: E402
    RuntimeConfigError,
    build_adapter_registry,
    load_provider_config,
    resolve_configured_adapter,
)


@dataclass
class InteractiveRuntime:
    """CLI-owned wiring for one interactive PersonaOS session."""

    session: RuntimeSession
    persona_entry: PersonaLibraryEntry
    provider_config: ProviderConfig


Printer = Callable[[str], None]
InputReader = Callable[[str], str]


def provider_config() -> ProviderConfig:
    """Load the runtime provider configuration."""

    return load_provider_config()


def configured_adapter(config: ProviderConfig):
    """Resolve the configured adapter through AdapterRegistry."""

    registry = build_adapter_registry(config, timeout=120.0)
    return resolve_configured_adapter(config, registry)


def build_persona_entry() -> PersonaLibraryEntry:
    """Build a valid in-memory persona lifecycle for the CLI session."""

    profile = PersonaProfile(
        name="PersonaOS Runtime Guide",
        traits={
            "focus": "clear local-first runtime conversation",
            "tone": "calm, concise, and helpful",
        },
        values=[
            "architectural boundaries",
            "replaceable providers",
            "temporary session history",
        ],
        style="structured, friendly, and precise",
        boundaries=[
            "do not claim durable writes",
            "do not mutate persona identity during runtime",
        ],
        thinking_patterns=[
            "separate persona, memory, knowledge, runtime, and provider logic",
        ],
        communication_style=[
            "answer naturally",
            "keep explanations concise",
        ],
    )
    version = PersonaVersion(
        id="interactive-runtime-guide-v1",
        persona_name=profile.name,
        version="1.0",
        created_at="2026-07-16",
        profile_snapshot={
            "name": profile.name,
            "traits": dict(profile.traits),
            "values": list(profile.values),
            "style": profile.style,
            "boundaries": list(profile.boundaries),
        },
        source_ids=["interactive-runtime-cli"],
        change_note="In-memory persona for CLI runtime.",
    )
    entry = PersonaLibraryEntry(
        id="interactive-runtime-guide",
        name=profile.name,
        description="In-memory CLI persona for PersonaOS runtime.",
        current_version_id=version.id,
        profile=profile,
        versions=[version],
        source_ids=["interactive-runtime-cli"],
    )
    entry.submit_for_review(
        reviewer="local-cli",
        notes="Prepared for interactive runtime.",
    )
    entry.approve(
        reviewer="local-cli",
        notes="Approved for local interactive runtime.",
    )
    PersonaActivationManager().activate(
        entry,
        activated_by="local-cli",
        activated_at="2026-07-16T00:00:00Z",
    )
    return entry


def build_persona_os_context(entry: PersonaLibraryEntry) -> PersonaOSContext:
    """Build a minimal prepared PersonaOSContext without durable writes."""

    memory = MemoryRecord(
        content=(
            "This CLI session uses temporary RuntimeSession conversation "
            "history only."
        ),
        category="working",
        confidence=0.9,
        importance=0.7,
        source="interactive-runtime-cli",
        timestamp="2026-07-16T00:00:00Z",
    )
    knowledge = KnowledgeRecord(
        content=(
            "PersonaOS runtime generation should preserve persona, memory, "
            "knowledge, prompt, session, and provider boundaries."
        ),
        category="architecture",
        source="docs/RUNTIME_ARCHITECTURE.md",
        confidence=0.95,
        timestamp="2026-07-16T00:00:00Z",
    )
    profile = entry.profile
    return PersonaOSContext(
        query="interactive runtime",
        persona=PersonaContext(
            name=entry.name,
            traits=list((profile.traits or {}).values()) if profile else [],
            values=list(profile.values) if profile else [],
            style=profile.style if profile else "",
        ),
        memories=MemoryContext(memories=[memory]),
        knowledge=KnowledgeContext(
            knowledge_records=[knowledge],
            sources=[knowledge.source],
        ),
        confidence=ConfidenceContext(
            score=0.9,
            factors={
                "interactive_cli": True,
                "temporary_session_history": True,
            },
        ),
    )


def build_runtime() -> InteractiveRuntime:
    """Wire existing runtime boundaries for the interactive CLI."""

    entry = build_persona_entry()
    if not entry.is_approved_for_activation():
        raise ChatRuntimeError("Persona is not approved.")
    if not entry.is_active():
        raise ChatRuntimeError("Persona is not active.")
    if not entry.has_valid_current_version():
        raise ChatRuntimeError("Persona current version is invalid.")

    library = PersonaLibraryEngine()
    library.add_persona(entry)
    selector = PersonaSelector(library)
    config = provider_config()
    adapter = configured_adapter(config)
    chat_runtime = ChatRuntime(
        persona_selector=selector,
        adapter=adapter,
        runtime_context_assembler=RuntimeContextAssembler(),
    )
    session = RuntimeSession(
        id="interactive-cli-session",
        persona_entry=entry,
        persona_os_context=build_persona_os_context(entry),
        chat_runtime=chat_runtime,
    )
    return InteractiveRuntime(
        session=session,
        persona_entry=entry,
        provider_config=config,
    )


def print_startup(runtime: InteractiveRuntime, printer: Printer = print) -> None:
    printer("PersonaOS Interactive Runtime")
    printer("")
    printer(f"Persona: {runtime.persona_entry.name}")
    printer(f"Provider: {runtime.provider_config.provider}")
    printer(f"Model: {runtime.provider_config.model}")
    printer("")
    printer("Type /help for commands.")
    printer("Type /exit to end the session.")


def print_help(printer: Printer = print) -> None:
    printer("Commands:")
    printer("  /help     Show available commands.")
    printer("  /history  Show temporary session conversation turns.")
    printer("  /clear    Clear temporary RuntimeSession history.")
    printer("  /status   Show persona, provider, model, and turn count.")
    printer("  /exit     End the session.")


def print_history(session: RuntimeSession, printer: Printer = print) -> None:
    history = session.get_history()
    if not history:
        printer("Temporary history is empty.")
        return

    for index, turn in enumerate(history, start=1):
        role = turn.get("role", "")
        content = turn.get("content", "")
        printer(f"{index}. {role}: {content}")


def print_status(runtime: InteractiveRuntime, printer: Printer = print) -> None:
    printer(f"Persona: {runtime.persona_entry.name}")
    printer(f"Provider: {runtime.provider_config.provider}")
    printer(f"Model: {runtime.provider_config.model}")
    printer(f"Temporary turns: {runtime.session.turn_count()}")


def handle_command(
    command: str,
    runtime: InteractiveRuntime,
    printer: Printer = print,
) -> bool:
    """Handle a CLI command. Return False when the loop should exit."""

    normalized = command.strip().lower()
    if normalized == "/help":
        print_help(printer)
        return True
    if normalized == "/exit":
        printer("Session ended.")
        return False
    if normalized == "/history":
        print_history(runtime.session, printer)
        return True
    if normalized == "/clear":
        runtime.session.clear_history()
        printer("Temporary history cleared.")
        return True
    if normalized == "/status":
        print_status(runtime, printer)
        return True

    printer(f"Unknown command: {command}")
    printer("Type /help for commands.")
    return True


def runtime_error_message(error: Exception) -> str:
    """Return a readable CLI error without exposing low-level stack traces."""

    if isinstance(error, EmptyUserInputError):
        return "Empty input was ignored."
    if isinstance(error, AssistantResponseError):
        return "The assistant returned an empty response."
    if isinstance(error, RuntimeSessionGenerationError):
        cause = error.__cause__
        if isinstance(cause, AdapterGenerationError):
            adapter_cause = cause.__cause__
            if isinstance(adapter_cause, OllamaTransportError):
                return (
                    "Ollama is unavailable at "
                    f"{runtime_provider_endpoint(error)}. "
                    "Please confirm Ollama is running locally."
                )
            if isinstance(adapter_cause, OllamaResponseError):
                return (
                    f"Model {runtime_provider_model(error)} did not return "
                    "usable content. Please confirm the model is available."
                )
        return "Runtime generation failed. No durable state was written."
    if isinstance(error, ChatRuntimeError):
        return f"Runtime error: {error}"

    return "Unexpected runtime error. No durable state was written."


def runtime_provider_endpoint(error: Exception) -> str:
    """Best-effort configured endpoint for readable provider errors."""

    config = runtime_provider_config_from_error(error)
    return config.endpoint if config is not None else "the configured endpoint"


def runtime_provider_model(error: Exception) -> str:
    """Best-effort configured model for readable provider errors."""

    config = runtime_provider_config_from_error(error)
    return config.model if config is not None else "the configured model"


def runtime_provider_config_from_error(error: Exception) -> ProviderConfig | None:
    cause = getattr(error, "__cause__", None)
    adapter_cause = getattr(cause, "__cause__", None)
    adapter = getattr(adapter_cause, "adapter", None)
    config = getattr(adapter, "config", None)
    if isinstance(config, ProviderConfig):
        return config

    try:
        return provider_config()
    except RuntimeConfigError:
        return None


def run_loop(
    runtime: InteractiveRuntime,
    input_reader: InputReader = input,
    printer: Printer = print,
) -> int:
    print_startup(runtime, printer)

    while True:
        try:
            user_input = input_reader("> ")
        except KeyboardInterrupt:
            printer("")
            printer("Session interrupted. Goodbye.")
            return 0
        except EOFError:
            printer("")
            printer("Session ended.")
            return 0

        if not user_input.strip():
            continue
        if user_input.strip().startswith("/"):
            if not handle_command(user_input, runtime, printer):
                return 0
            continue

        try:
            response = runtime.session.send(user_input)
        except Exception as exc:
            printer(runtime_error_message(exc))
            continue

        printer("")
        printer(response.content)
        printer("")


def main() -> int:
    try:
        runtime = build_runtime()
    except ChatRuntimeError as exc:
        print(f"Persona lifecycle validation failed: {exc}")
        return 1
    except RuntimeConfigError as exc:
        print(f"Runtime configuration failed: {exc}")
        return 1

    return run_loop(runtime)


if __name__ == "__main__":
    raise SystemExit(main())
