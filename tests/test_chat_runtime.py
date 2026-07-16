"""Tests for controlled ChatRuntime boundary."""

import copy

import pytest

from backend.adapters import BaseLLMAdapter
from backend.core import (
    PersonaActivationManager,
    PersonaLibraryEngine,
    PersonaSelector,
)
from backend.core.knowledge import KnowledgeRecord
from backend.models import (
    LLMResponse,
    PersonaActivation,
    PersonaActivationStatus,
    PersonaLibraryEntry,
    PersonaProfile,
    PersonaVersion,
    RuntimeContext,
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
    AdapterGenerationError,
    AdapterUnavailableError,
    ChatRuntime,
    EmptyUserInputError,
    InvalidPersonaVersionError,
    PersonaInactiveError,
    PersonaNotSelectableError,
)


class FakeAdapter(BaseLLMAdapter):
    def __init__(
        self,
        response: LLMResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response or LLMResponse(
            content="generated reply",
            provider="fake",
            model="fake-model",
        )
        self.error = error
        self.calls: list[dict] = []

    def generate(
        self,
        runtime_context: RuntimeContext,
        user_input: str,
    ) -> LLMResponse:
        self.calls.append(
            {
                "runtime_context": runtime_context,
                "user_input": user_input,
            }
        )
        if self.error is not None:
            raise self.error

        return self.response


class TrackingRuntimeContextAssembler:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def assemble(
        self,
        context: PersonaOSContext,
        skills: list | None = None,
        persona_version: str = "",
        metadata: dict | None = None,
    ) -> RuntimeContext:
        self.calls.append(
            {
                "context": context,
                "skills": skills,
                "persona_version": persona_version,
                "metadata": metadata,
            }
        )
        return RuntimeContext(
            active_persona=context.persona,
            persona_version=persona_version,
            memories=context.memories.memories,
            knowledge={
                "records": context.knowledge.knowledge_records,
                "sources": context.knowledge.sources,
            },
            skills=skills or [],
            confidence=context.confidence,
            metadata=dict(metadata or {}),
        )


def make_profile() -> PersonaProfile:
    return PersonaProfile(
        name="Architect",
        traits={"focus": "runtime boundaries"},
        values=["clarity"],
        style="precise",
        boundaries=["do not mutate durable state"],
    )


def make_version(version_id: str = "architect-version-1") -> PersonaVersion:
    return PersonaVersion(
        id=version_id,
        persona_name="Architect",
        version="1.0",
        created_at="2026-07-16",
        profile_snapshot={"name": "Architect", "style": "precise"},
        source_ids=["source-1"],
        change_note="Initial runtime version.",
    )


def make_entry(
    *,
    approved: bool = True,
    active: bool = True,
    reviewing: bool = False,
    rejected: bool = False,
    valid_version: bool = True,
) -> PersonaLibraryEntry:
    version = make_version()
    entry = PersonaLibraryEntry(
        id="architect",
        name="Architect",
        current_version_id=version.id if valid_version else "missing-version",
        profile=make_profile(),
        versions=[version],
    )

    if reviewing:
        entry.submit_for_review(reviewer="Morgan")
    if approved:
        entry.submit_for_review(reviewer="Morgan")
        entry.approve(reviewer="Morgan")
    if rejected:
        entry.submit_for_review(reviewer="Morgan")
        entry.reject(reviewer="Morgan")
    if active and approved and valid_version:
        PersonaActivationManager().activate(entry, activated_by="Morgan")
    if active and approved and not valid_version:
        entry.activations.append(
            PersonaActivation(
                activation_id="manual-active-invalid-version",
                persona_entry_id=entry.id,
                persona_version_id=entry.current_version_id,
                status=PersonaActivationStatus.ACTIVE,
            )
        )

    return entry


def make_runtime(
    entry: PersonaLibraryEntry,
    adapter: BaseLLMAdapter | None = None,
    assembler: TrackingRuntimeContextAssembler | None = None,
) -> tuple[ChatRuntime, PersonaLibraryEngine, TrackingRuntimeContextAssembler]:
    library = PersonaLibraryEngine()
    library.add_persona(entry)
    selector = PersonaSelector(library)
    runtime_assembler = assembler or TrackingRuntimeContextAssembler()
    runtime = ChatRuntime(
        persona_selector=selector,
        adapter=adapter or FakeAdapter(),
        runtime_context_assembler=runtime_assembler,
    )
    return runtime, library, runtime_assembler


def make_context() -> PersonaOSContext:
    memory = MemoryRecord(
        content="Runtime generation should preserve memory records.",
        category="semantic",
        confidence=0.8,
        importance=0.9,
        source="test-memory",
        timestamp="2026-07-16T00:00:00Z",
    )
    knowledge = KnowledgeRecord(
        content="ChatRuntime coordinates existing runtime boundaries.",
        category="architecture",
        source="test-knowledge",
        confidence=0.95,
        timestamp="2026-07-16T00:00:00Z",
    )
    return PersonaOSContext(
        query="runtime generation",
        persona=PersonaContext(
            name="Architect",
            traits=["focused"],
            values=["clarity"],
            style="precise",
        ),
        memories=MemoryContext(memories=[memory]),
        knowledge=KnowledgeContext(
            knowledge_records=[knowledge],
            sources=[knowledge.source],
        ),
        confidence=ConfidenceContext(score=0.88),
    )


def test_approved_active_persona_with_valid_version_can_generate_reply() -> None:
    entry = make_entry()
    response = LLMResponse(content="preserved reply", provider="fake")
    adapter = FakeAdapter(response=response)
    runtime, _, _ = make_runtime(entry, adapter=adapter)

    result = runtime.generate_reply(
        "hello",
        entry,
        make_context(),
    )

    assert result is response
    assert result.content == "preserved reply"


def test_draft_persona_is_rejected() -> None:
    entry = make_entry(approved=False, active=False)
    runtime, _, _ = make_runtime(entry)

    with pytest.raises(PersonaNotSelectableError):
        runtime.generate_reply("hello", entry, make_context())


def test_reviewing_persona_is_rejected() -> None:
    entry = make_entry(
        approved=False,
        active=False,
        reviewing=True,
    )
    runtime, _, _ = make_runtime(entry)

    with pytest.raises(PersonaNotSelectableError):
        runtime.generate_reply("hello", entry, make_context())


def test_rejected_persona_is_rejected() -> None:
    entry = make_entry(
        approved=False,
        active=False,
        rejected=True,
    )
    runtime, _, _ = make_runtime(entry)

    with pytest.raises(PersonaNotSelectableError):
        runtime.generate_reply("hello", entry, make_context())


def test_approved_inactive_persona_is_rejected() -> None:
    entry = make_entry(active=False)
    runtime, _, _ = make_runtime(entry)

    with pytest.raises(PersonaInactiveError):
        runtime.generate_reply("hello", entry, make_context())


def test_persona_with_invalid_current_version_is_rejected() -> None:
    entry = make_entry(valid_version=False)
    runtime, _, _ = make_runtime(entry)

    with pytest.raises(InvalidPersonaVersionError):
        runtime.generate_reply("hello", entry, make_context())


def test_runtime_context_assembler_is_used() -> None:
    entry = make_entry()
    adapter = FakeAdapter()
    runtime, _, assembler = make_runtime(entry, adapter=adapter)
    context = make_context()

    runtime.generate_reply("hello", entry, context)

    assert len(assembler.calls) == 1
    assert assembler.calls[0]["context"] is context
    assert assembler.calls[0]["persona_version"] == entry.current_version_id
    assert assembler.calls[0]["metadata"]["persona_entry_id"] == entry.id


def test_selected_adapter_is_called_exactly_once() -> None:
    entry = make_entry()
    adapter = FakeAdapter()
    runtime, _, _ = make_runtime(entry, adapter=adapter)

    runtime.generate_reply("hello", entry, make_context())

    assert len(adapter.calls) == 1


def test_user_input_is_passed_correctly() -> None:
    entry = make_entry()
    adapter = FakeAdapter()
    runtime, _, _ = make_runtime(entry, adapter=adapter)

    runtime.generate_reply("hello runtime", entry, make_context())

    assert adapter.calls[0]["user_input"] == "hello runtime"


def test_returned_llm_response_is_preserved() -> None:
    entry = make_entry()
    response = LLMResponse(
        content="unchanged",
        metadata={"trace": "same-object"},
        provider="fake",
        model="fake-model",
        usage={"tokens": 3},
    )
    runtime, _, _ = make_runtime(entry, adapter=FakeAdapter(response=response))

    result = runtime.generate_reply("hello", entry, make_context())

    assert result is response


def test_runtime_generation_does_not_mutate_source_records() -> None:
    entry = make_entry()
    context = make_context()
    profile_before = copy.deepcopy(entry.profile.__dict__)
    version_before = copy.deepcopy(entry.versions[0].__dict__)
    entry_before = {
        "current_version_id": entry.current_version_id,
        "lifecycle_state": entry.lifecycle_state,
        "review_status": entry.review_status,
        "activations": copy.deepcopy([a.__dict__ for a in entry.activations]),
        "reviews": copy.deepcopy([r.__dict__ for r in entry.reviews]),
    }
    memory = context.memories.memories[0]
    knowledge = context.knowledge.knowledge_records[0]
    memory_before = copy.deepcopy(memory.__dict__)
    knowledge_before = copy.deepcopy(knowledge.__dict__)
    runtime, _, _ = make_runtime(entry)

    runtime.generate_reply("hello", entry, context)

    assert entry.profile.__dict__ == profile_before
    assert entry.versions[0].__dict__ == version_before
    assert entry.current_version_id == entry_before["current_version_id"]
    assert entry.lifecycle_state == entry_before["lifecycle_state"]
    assert entry.review_status == entry_before["review_status"]
    assert [a.__dict__ for a in entry.activations] == entry_before[
        "activations"
    ]
    assert [r.__dict__ for r in entry.reviews] == entry_before["reviews"]
    assert memory.__dict__ == memory_before
    assert knowledge.__dict__ == knowledge_before


def test_adapter_failure_is_normalized_at_runtime_boundary() -> None:
    entry = make_entry()
    adapter = FakeAdapter(error=RuntimeError("provider detail"))
    runtime, _, _ = make_runtime(entry, adapter=adapter)

    with pytest.raises(AdapterGenerationError) as exc_info:
        runtime.generate_reply("hello", entry, make_context())

    assert str(exc_info.value) == "Adapter generation failed."


def test_empty_user_input_is_rejected() -> None:
    entry = make_entry()
    runtime, _, _ = make_runtime(entry)

    with pytest.raises(EmptyUserInputError):
        runtime.generate_reply("   ", entry, make_context())


def test_missing_adapter_is_rejected() -> None:
    entry = make_entry()
    runtime, _, _ = make_runtime(entry, adapter=FakeAdapter())
    runtime.adapter = None

    with pytest.raises(AdapterUnavailableError):
        runtime.generate_reply("hello", entry, make_context())
