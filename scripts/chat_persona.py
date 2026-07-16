"""Minimal local PersonaOS interactive runtime CLI."""

from __future__ import annotations

import argparse
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
    PersonaPackageError,
    PersonaPackageLoader,
    PersonaSelector,
)
from backend.core.knowledge import KnowledgeRecord  # noqa: E402
from backend.engine.runtime_context_assembler import (  # noqa: E402
    RuntimeContextAssembler,
)
from backend.models import (  # noqa: E402
    PersonaPackage,
    PersonaLibraryEntry,
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
    load_default_persona_package_id,
    load_provider_config,
    resolve_configured_adapter,
)


DEFAULT_PERSONA_PACKAGE_PATH = PROJECT_ROOT / "personas" / "architect"
DEFAULT_PERSONAS_DIR = PROJECT_ROOT / "personas"


@dataclass
class InteractiveRuntime:
    """CLI-owned wiring for one interactive PersonaOS session."""

    session: RuntimeSession
    persona_entry: PersonaLibraryEntry
    provider_config: ProviderConfig
    personas_dir: Path = DEFAULT_PERSONAS_DIR


Printer = Callable[[str], None]
InputReader = Callable[[str], str]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI-owned arguments for interactive startup."""

    parser = argparse.ArgumentParser(
        description="Start the local PersonaOS interactive runtime."
    )
    parser.add_argument(
        "--persona",
        metavar="PACKAGE_ID",
        help=(
            "Persona package id to use for this session. "
            "Overrides config/runtime.json default_persona."
        ),
    )
    return parser.parse_args(argv)


def provider_config() -> ProviderConfig:
    """Load the runtime provider configuration."""

    return load_provider_config()


def default_persona_package_id() -> str:
    """Load the configured default persona package id."""

    return load_default_persona_package_id()


def default_persona_package_path() -> Path:
    """Resolve the configured default persona package path."""

    return DEFAULT_PERSONAS_DIR / default_persona_package_id()


def configured_adapter(config: ProviderConfig):
    """Resolve the configured adapter through AdapterRegistry."""

    registry = build_adapter_registry(config, timeout=120.0)
    return resolve_configured_adapter(config, registry)


def build_draft_persona_entry(
    package_path: Path | None = None,
) -> PersonaLibraryEntry:
    """Load the default persona package into a draft library entry."""

    resolved_package_path = package_path or default_persona_package_path()
    loader = PersonaPackageLoader()
    package = loader.load(resolved_package_path)
    return loader.to_library_entry(
        package,
        created_at="2026-07-16",
        change_note="Loaded from local CLI persona package.",
    )


def discover_persona_packages(
    personas_dir: Path = DEFAULT_PERSONAS_DIR,
) -> list[PersonaLibraryEntry]:
    """Return draft entries for valid package directories."""

    if not personas_dir.exists():
        return []

    loader = PersonaPackageLoader()
    entries: list[PersonaLibraryEntry] = []
    for package_path in sorted(personas_dir.iterdir(), key=lambda path: path.name):
        if not package_path.is_dir():
            continue
        if not loader.validate(package_path).is_valid:
            continue
        package = loader.load(package_path)
        entries.append(
            loader.to_library_entry(
                package,
                created_at="2026-07-16",
                change_note="Discovered from local CLI persona package.",
            )
        )
    return entries


def load_persona_package_by_id(
    personas_dir: Path,
    package_id: str,
) -> PersonaPackage:
    """Load a valid local persona package by package id."""

    package_id = package_id.strip()
    if not package_id:
        raise PersonaPackageError("Persona package id cannot be empty.")

    package_path = personas_dir / package_id
    if not package_path.is_dir():
        raise PersonaPackageError(f"Persona package not found: {package_id}")

    loader = PersonaPackageLoader()
    return loader.load(package_path)


def approve_persona_for_cli_runtime(
    entry: PersonaLibraryEntry,
) -> PersonaLibraryEntry:
    """Approve and activate a package-derived entry for this CLI process only."""

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


def prepare_persona_for_cli_runtime(
    package_path: Path,
) -> PersonaLibraryEntry:
    """Load, approve, and activate a package-derived entry in memory."""

    return approve_persona_for_cli_runtime(
        build_draft_persona_entry(package_path)
    )


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


def build_runtime(
    persona_package_path: Path | None = None,
) -> InteractiveRuntime:
    """Wire existing runtime boundaries for the interactive CLI."""

    resolved_package_path = persona_package_path or default_persona_package_path()
    entry = prepare_persona_for_cli_runtime(resolved_package_path)
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
        personas_dir=resolved_package_path.parent,
    )


def persona_package_path_from_id(package_id: str | None) -> Path | None:
    """Resolve an optional package id into a local persona package path."""

    if package_id is None:
        return None
    package_id = package_id.strip()
    if not package_id:
        raise PersonaPackageError("Persona package id cannot be empty.")

    return DEFAULT_PERSONAS_DIR / package_id


def switch_persona(
    runtime: InteractiveRuntime,
    package_id: str,
) -> bool:
    """Switch the active CLI persona to another package in memory."""

    package_path = runtime.personas_dir / package_id
    if not package_path.is_dir():
        return False

    entry = prepare_persona_for_cli_runtime(package_path)
    library = PersonaLibraryEngine()
    library.add_persona(entry)
    selector = PersonaSelector(library)
    adapter = configured_adapter(runtime.provider_config)
    chat_runtime = ChatRuntime(
        persona_selector=selector,
        adapter=adapter,
        runtime_context_assembler=RuntimeContextAssembler(),
    )
    runtime.persona_entry = entry
    runtime.session = RuntimeSession(
        id=f"interactive-cli-session-{entry.id or package_id}",
        persona_entry=entry,
        persona_os_context=build_persona_os_context(entry),
        chat_runtime=chat_runtime,
    )
    return True


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
    printer("  /persona list")
    printer("            Show valid local persona packages.")
    printer("  /persona info <package_id>")
    printer("            Show local persona package details.")
    printer("  /persona use <package_id>")
    printer("            Switch the active persona package for this session.")
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
    printer(f"Persona package: {runtime.persona_entry.id}")
    printer(f"Provider: {runtime.provider_config.provider}")
    printer(f"Model: {runtime.provider_config.model}")
    printer(f"Temporary turns: {runtime.session.turn_count()}")


def print_persona_packages(
    personas_dir: Path,
    current_persona_id: str,
    printer: Printer = print,
) -> None:
    entries = discover_persona_packages(personas_dir)
    if not entries:
        printer("No valid persona packages found.")
        return

    printer("Available persona packages:")
    for entry in entries:
        marker = "*" if entry.id == current_persona_id else " "
        version = entry.current_version_id.split(":", 1)[1]
        description = entry.description or ""
        printer(f"{marker} {entry.id}  {entry.name}  v{version}  {description}")


def print_persona_package_info(
    personas_dir: Path,
    package_id: str,
    printer: Printer = print,
) -> None:
    """Print deterministic local persona package metadata."""

    package = load_persona_package_by_id(personas_dir, package_id)
    profile = package.profile
    printer(f"Package: {package.manifest.package_id}")
    printer(f"Name: {package.manifest.name}")
    printer(f"Version: {package.manifest.version}")
    printer(f"Description: {package.manifest.description}")
    if profile is not None:
        printer(f"Style: {profile.style}")
        printer("Values:")
        for value in profile.values:
            printer(f"  - {value}")
        printer("Boundaries:")
        for boundary in profile.boundaries:
            printer(f"  - {boundary}")
    printer(f"Examples: {len(package.examples)}")
    printer(f"Sources: {len(package.sources)}")


def handle_persona_command(
    command: str,
    runtime: InteractiveRuntime,
    printer: Printer = print,
) -> bool:
    parts = command.strip().split()
    if len(parts) == 2 and parts[1].lower() == "list":
        print_persona_packages(
            runtime.personas_dir,
            runtime.persona_entry.id,
            printer,
        )
        return True

    if len(parts) == 3 and parts[1].lower() == "info":
        try:
            print_persona_package_info(
                runtime.personas_dir,
                parts[2],
                printer,
            )
        except PersonaPackageError as exc:
            printer(f"Persona package loading failed: {exc}")
        return True

    if len(parts) == 3 and parts[1].lower() == "use":
        package_id = parts[2]
        try:
            switched = switch_persona(runtime, package_id)
        except PersonaPackageError as exc:
            printer(f"Persona package loading failed: {exc}")
            return True
        if not switched:
            printer(f"Persona package not found: {package_id}")
            return True
        printer(f"Switched persona to: {runtime.persona_entry.name}")
        return True

    printer("Usage:")
    printer("  /persona list")
    printer("  /persona info <package_id>")
    printer("  /persona use <package_id>")
    return True


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
    if normalized.startswith("/persona"):
        return handle_persona_command(command, runtime, printer)

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


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        runtime = build_runtime(
            persona_package_path_from_id(args.persona)
        )
    except ChatRuntimeError as exc:
        print(f"Persona lifecycle validation failed: {exc}")
        return 1
    except RuntimeConfigError as exc:
        print(f"Runtime configuration failed: {exc}")
        return 1
    except PersonaPackageError as exc:
        print(f"Persona package loading failed: {exc}")
        return 1

    return run_loop(runtime)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
