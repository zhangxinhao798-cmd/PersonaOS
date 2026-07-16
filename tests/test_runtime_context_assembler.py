"""Tests for RuntimeContextAssembler."""

from backend.core.knowledge import KnowledgeRecord
from backend.core.skill import SkillRecord
from backend.engine.persona_os import PersonaOS
from backend.engine.runtime_context_assembler import RuntimeContextAssembler
from backend.models.context import (
    ConfidenceContext,
    KnowledgeContext,
    MemoryContext,
    PersonaContext,
    PersonaOSContext,
)
from backend.models.memory_record import MemoryRecord
from backend.models.runtime_context import RuntimeContext


def make_memory() -> MemoryRecord:
    return MemoryRecord(
        content="Runtime assembly should preserve boundaries.",
        category="semantic",
        confidence=0.8,
        importance=0.7,
        source="test-memory",
        timestamp="2026-07-16T00:00:00Z",
    )


def make_knowledge() -> KnowledgeRecord:
    return KnowledgeRecord(
        content="Runtime context is assembled after internal retrieval.",
        category="architecture",
        source="test-knowledge",
        confidence=0.9,
        timestamp="2026-07-16T00:00:00Z",
    )


def make_skill() -> SkillRecord:
    return SkillRecord(
        name="context_inspection",
        description="Inspect prepared context boundaries.",
        category="runtime",
        confidence=0.85,
        metadata={"permission": "read"},
    )


def test_assembles_runtime_context_from_existing_components() -> None:
    persona_os = PersonaOS()
    persona_os.persona_engine.set_trait("focus", "runtime boundaries")
    memory = persona_os.memory_engine.create_memory(make_memory())
    knowledge = persona_os.knowledge_engine.create_knowledge(make_knowledge())
    skill = make_skill()

    internal_context = persona_os.process_context("runtime context assembly")
    runtime_context = RuntimeContextAssembler().assemble(
        internal_context,
        skills=[skill],
        persona_version="v1",
        metadata={"runtime_stage": "assembly"},
    )

    assert isinstance(runtime_context, RuntimeContext)
    assert runtime_context.active_persona.name == "Default Persona"
    assert runtime_context.persona_version == "v1"
    assert runtime_context.memories == [memory]
    assert runtime_context.knowledge["records"] == [knowledge]
    assert runtime_context.knowledge["sources"] == ["test-knowledge"]
    assert runtime_context.skills == [skill]
    assert runtime_context.confidence.score == internal_context.confidence.score
    assert len(runtime_context.fusion_context) == 1
    assert runtime_context.metadata["query"] == "runtime context assembly"
    assert runtime_context.metadata["runtime_stage"] == "assembly"


def test_missing_optional_data_defaults_to_empty_boundaries() -> None:
    runtime_context = RuntimeContextAssembler().assemble(
        PersonaOSContext(
            query="empty runtime",
            persona=PersonaContext(name="Minimal"),
            memories=None,
            fusion_memory=None,
            knowledge=None,
            confidence=None,
        )
    )

    assert runtime_context.active_persona.name == "Minimal"
    assert runtime_context.memories == []
    assert runtime_context.knowledge == {
        "records": [],
        "sources": [],
    }
    assert runtime_context.skills == []
    assert runtime_context.confidence is None
    assert runtime_context.fusion_context == []
    assert runtime_context.expression == {}
    assert runtime_context.metadata["query"] == "empty runtime"


def test_runtime_context_preserves_source_boundaries() -> None:
    memory = make_memory()
    knowledge = make_knowledge()
    confidence = ConfidenceContext(
        score=0.75,
        factors={"memory_count": 1, "knowledge_count": 1},
    )
    internal_context = PersonaOSContext(
        query="boundary preservation",
        persona=PersonaContext(name="Boundary Tester"),
        memories=MemoryContext(memories=[memory]),
        knowledge=KnowledgeContext(
            knowledge_records=[knowledge],
            sources=[knowledge.source],
        ),
        confidence=confidence,
    )
    setattr(
        internal_context,
        "metadata",
        {"expression": {"catchphrases": ["Keep the boundary."]}},
    )

    runtime_context = RuntimeContextAssembler().assemble(internal_context)

    assert runtime_context.active_persona is internal_context.persona
    assert runtime_context.memories is internal_context.memories.memories
    assert (
        runtime_context.knowledge["records"]
        is internal_context.knowledge.knowledge_records
    )
    assert runtime_context.confidence is confidence
    assert runtime_context.expression == {
        "catchphrases": ["Keep the boundary."]
    }
    assert "source_boundaries" in runtime_context.metadata
    assert runtime_context.metadata["source_boundaries"]["memories"] == (
        "PersonaOSContext.memories"
    )
