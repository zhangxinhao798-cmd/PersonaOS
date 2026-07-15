"""PersonaOS integration tests for persona-memory fusion."""

from backend.engine.persona_os import PersonaOS
from backend.fusion import PersonaMemoryFusion
from backend.models.context import PersonaOSContext
from backend.models.memory_record import MemoryRecord


def make_memory() -> MemoryRecord:
    return MemoryRecord(
        content="Architecture decisions should preserve modular boundaries.",
        category="semantic",
        confidence=0.8,
        importance=0.7,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )


def memory_state(memory: MemoryRecord) -> tuple:
    return (
        memory.content,
        memory.category,
        memory.confidence,
        memory.importance,
        memory.source,
        memory.timestamp,
        memory.state,
    )


def test_persona_os_initializes_with_fusion_layer() -> None:
    persona_os = PersonaOS()

    assert isinstance(persona_os.persona_memory_fusion, PersonaMemoryFusion)


def test_process_context_returns_context_with_fusion_results() -> None:
    persona_os = PersonaOS()
    persona_os.persona_engine.set_trait(
        "focus",
        "architecture modular boundaries",
    )
    persona_os.memory_engine.create_memory(make_memory())

    context = persona_os.process_context("Review architecture decisions")

    assert isinstance(context, PersonaOSContext)
    assert len(context.fusion_memory.fusions) == 1


def test_fusion_results_exist_for_retrieved_memories() -> None:
    persona_os = PersonaOS()
    persona_os.persona_engine.set_trait(
        "focus",
        "architecture modular boundaries",
    )
    memory = persona_os.memory_engine.create_memory(make_memory())

    context = persona_os.process_context("Review architecture decisions")
    fusion = context.fusion_memory.fusions[0]

    assert fusion.memory_content == memory.content
    assert fusion.persona_name == "Default Persona"
    assert fusion.relevance_score > 0.0


def test_original_memory_remains_unchanged_after_fusion() -> None:
    persona_os = PersonaOS()
    persona_os.persona_engine.set_trait(
        "focus",
        "architecture modular boundaries",
    )
    memory = persona_os.memory_engine.create_memory(make_memory())
    original_state = memory_state(memory)

    persona_os.process_context("Review architecture decisions")

    assert memory_state(memory) == original_state
