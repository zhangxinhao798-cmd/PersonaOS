"""Manual live smoke test for the controlled PersonaOS ChatRuntime path.

This script exercises:

approved active PersonaLibraryEntry -> PersonaSelector -> PersonaOSContext
-> RuntimeContextAssembler -> ChatRuntime -> OllamaAdapter -> local Ollama
-> qwen3:14b -> LLMResponse

It does not write durable PersonaOS state, persist conversation history, or
create durable memories.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.adapters import (  # noqa: E402
    BaseLLMAdapter,
    OllamaAdapter,
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
    LLMResponse,
    PersonaLibraryEntry,
    PersonaProfile,
    PersonaVersion,
    ProviderConfig,
    RuntimeContext,
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
    ChatRuntime,
    ChatRuntimeError,
)


class InstrumentedRuntimeContextAssembler(RuntimeContextAssembler):
    """Track that ChatRuntime delegated runtime context assembly."""

    def __init__(self) -> None:
        self.calls = 0

    def assemble(
        self,
        context: PersonaOSContext,
        skills: list | None = None,
        persona_version: str = "",
        metadata: dict | None = None,
    ) -> RuntimeContext:
        self.calls += 1
        return super().assemble(
            context,
            skills=skills,
            persona_version=persona_version,
            metadata=metadata,
        )


class InstrumentedAdapter(BaseLLMAdapter):
    """Track that the real OllamaAdapter is reached through ChatRuntime."""

    def __init__(self, adapter: OllamaAdapter) -> None:
        self.adapter = adapter
        self.calls = 0
        self.provider = adapter.provider
        self.config = adapter.config

    def generate(
        self,
        runtime_context: RuntimeContext,
        user_input: str,
    ) -> LLMResponse:
        self.calls += 1
        return self.adapter.generate(runtime_context, user_input)


def build_persona_entry() -> PersonaLibraryEntry:
    profile = PersonaProfile(
        name="PersonaOS Runtime Architect",
        traits={
            "focus": "clear architecture boundaries",
            "tone": "calm and precise",
        },
        values=[
            "local-first operation",
            "replaceable providers",
            "durable identity boundaries",
        ],
        style="concise, structured, and careful",
        boundaries=[
            "do not claim persistence when none exists",
            "do not mutate durable persona state during runtime generation",
        ],
        thinking_patterns=[
            "separate identity, memory, knowledge, and provider transport",
        ],
        communication_style=[
            "answer directly",
            "name architectural boundaries",
        ],
    )
    version = PersonaVersion(
        id="runtime-architect-v1",
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
        source_ids=["manual-smoke-source"],
        change_note="Manual ChatRuntime smoke persona.",
    )
    entry = PersonaLibraryEntry(
        id="runtime-architect",
        name=profile.name,
        description="Manual smoke-test persona for controlled ChatRuntime.",
        current_version_id=version.id,
        profile=profile,
        versions=[version],
        source_ids=["manual-smoke-source"],
    )

    entry.submit_for_review(
        reviewer="manual-smoke",
        notes="Prepared for controlled ChatRuntime smoke test.",
    )
    entry.approve(
        reviewer="manual-smoke",
        notes="Approved for local runtime smoke test.",
    )
    PersonaActivationManager().activate(
        entry,
        activated_by="manual-smoke",
        activated_at="2026-07-16T00:00:00Z",
    )
    return entry


def build_persona_os_context() -> PersonaOSContext:
    memory = MemoryRecord(
        content=(
            "PersonaOS is validating the controlled ChatRuntime path without "
            "writing durable memory."
        ),
        category="working",
        confidence=0.9,
        importance=0.8,
        source="manual-chat-runtime-smoke",
        timestamp="2026-07-16T00:00:00Z",
    )
    knowledge = KnowledgeRecord(
        content=(
            "Runtime generation must preserve persona, memory, knowledge, "
            "and provider boundaries."
        ),
        category="architecture",
        source="docs/RUNTIME_ARCHITECTURE.md",
        confidence=0.95,
        timestamp="2026-07-16T00:00:00Z",
    )

    return PersonaOSContext(
        query="请用你的人格风格简单介绍一下自己。",
        persona=PersonaContext(
            name="PersonaOS Runtime Architect",
            traits=["clear architecture boundaries", "calm precision"],
            values=["local-first", "replaceable providers"],
            style="concise, structured, and careful",
        ),
        memories=MemoryContext(memories=[memory]),
        knowledge=KnowledgeContext(
            knowledge_records=[knowledge],
            sources=[knowledge.source],
        ),
        confidence=ConfidenceContext(
            score=0.9,
            factors={
                "manual_smoke": True,
                "no_durable_writes": True,
            },
        ),
    )


def snapshot_entry(entry: PersonaLibraryEntry) -> dict[str, Any]:
    return {
        "profile": deepcopy(entry.profile.__dict__ if entry.profile else None),
        "versions": deepcopy([version.__dict__ for version in entry.versions]),
        "entry": {
            "id": entry.id,
            "name": entry.name,
            "description": entry.description,
            "lifecycle_state": entry.lifecycle_state,
            "review_status": entry.review_status,
            "current_version_id": entry.current_version_id,
            "source_ids": list(entry.source_ids),
            "traits": list(entry.traits),
        },
        "reviews": deepcopy([review.__dict__ for review in entry.reviews]),
        "activations": deepcopy(
            [activation.__dict__ for activation in entry.activations]
        ),
    }


def state_unchanged(entry: PersonaLibraryEntry, before: dict[str, Any]) -> bool:
    return snapshot_entry(entry) == before


def validate_lifecycle(entry: PersonaLibraryEntry) -> bool:
    checks = {
        "approved": entry.is_approved_for_activation(),
        "active": entry.is_active(),
        "valid_current_version": entry.has_valid_current_version(),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        print("Persona lifecycle validation failed:")
        for name in failed:
            print(f"  - {name}")
        return False

    print("Persona lifecycle validation:")
    for name in checks:
        print(f"  {name}: true")
    return True


def main() -> int:
    entry = build_persona_entry()
    if not validate_lifecycle(entry):
        return 1

    context = build_persona_os_context()
    before = snapshot_entry(entry)
    library = PersonaLibraryEngine()
    library.add_persona(entry)
    selector = PersonaSelector(library)
    selected = selector.select(entry.id)
    selector.clear()
    if selected is not entry:
        print("PersonaSelector rejected the approved active persona.")
        return 1

    config = ProviderConfig(
        provider="ollama",
        model="qwen3:14b",
        endpoint="http://localhost:11434",
    )
    ollama_adapter = OllamaAdapter(config=config, timeout=120.0)
    adapter = InstrumentedAdapter(ollama_adapter)
    assembler = InstrumentedRuntimeContextAssembler()
    runtime = ChatRuntime(
        persona_selector=selector,
        adapter=adapter,
        runtime_context_assembler=assembler,
    )
    user_input = "请用你的人格风格简单介绍一下自己。"

    try:
        response = runtime.generate_reply(user_input, entry, context)
    except AdapterGenerationError as exc:
        cause = exc.__cause__
        if isinstance(cause, OllamaTransportError):
            print(
                "Ollama is unavailable at http://localhost:11434, or the "
                "endpoint returned a non-success response. Please confirm "
                "Ollama is running locally."
            )
            return 1
        if isinstance(cause, OllamaResponseError):
            print(
                "Ollama responded, but qwen3:14b did not return usable "
                "generated content. Please confirm the configured model is "
                "available."
            )
            return 1

        print("ChatRuntime adapter generation failed cleanly.")
        return 1
    except ChatRuntimeError as exc:
        print(f"ChatRuntime validation failed: {exc}")
        return 1

    if not isinstance(response, LLMResponse):
        print("ChatRuntime did not return an LLMResponse.")
        return 1

    unchanged = state_unchanged(entry, before)
    print(f"selected persona: {entry.name}")
    print(f"persona_selector_accepted: {selected is entry}")
    print("chat_runtime_used: true")
    print(f"runtime_context_assembler_used: {assembler.calls == 1}")
    print(f"ollama_adapter_reached: {adapter.calls == 1}")
    print(f"llm_response_returned: {isinstance(response, LLMResponse)}")
    print(f"provider: {response.provider}")
    print(f"model: {response.model}")
    print("response:")
    print(response.content)

    if response.usage:
        print("usage:")
        for key, value in response.usage.items():
            print(f"  {key}: {value}")
    else:
        print("usage: {}")

    print(f"durable_persona_state_unchanged: {unchanged}")
    return 0 if unchanged else 1


if __name__ == "__main__":
    raise SystemExit(main())

