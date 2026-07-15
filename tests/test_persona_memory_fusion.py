"""Tests for persona-memory fusion coordination."""

from backend.fusion import PersonaMemoryFusion
from backend.models.fusion import FusionContext
from backend.models.memory_record import MemoryRecord
from backend.models.persona_profile import PersonaProfile


def make_memory() -> MemoryRecord:
    return MemoryRecord(
        content="Architecture decisions should preserve modular boundaries.",
        category="semantic",
        confidence=0.8,
        importance=0.7,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )


def make_persona(name: str, traits: dict[str, str]) -> PersonaProfile:
    return PersonaProfile(
        name=name,
        traits=traits,
        values=[],
        style="",
        boundaries=[],
    )


def test_fusion_returns_fusion_context() -> None:
    fusion = PersonaMemoryFusion()
    persona = make_persona(
        "Architect",
        {"focus": "architecture modular boundaries"},
    )

    result = fusion.fuse(persona, make_memory())

    assert isinstance(result, FusionContext)
    assert result.persona_name == "Architect"
    assert result.memory_content == (
        "Architecture decisions should preserve modular boundaries."
    )


def test_related_persona_produces_higher_relevance() -> None:
    fusion = PersonaMemoryFusion()
    memory = make_memory()
    related_persona = make_persona(
        "Architect",
        {"focus": "architecture modular boundaries"},
    )
    unrelated_persona = make_persona(
        "Chef",
        {"focus": "cooking recipes flavor"},
    )

    related_result = fusion.fuse(related_persona, memory)
    unrelated_result = fusion.fuse(unrelated_persona, memory)

    assert related_result.relevance_score > unrelated_result.relevance_score


def test_unrelated_persona_produces_lower_relevance() -> None:
    fusion = PersonaMemoryFusion()
    unrelated_persona = make_persona(
        "Chef",
        {"focus": "cooking recipes flavor"},
    )

    result = fusion.fuse(unrelated_persona, make_memory())

    assert result.relevance_score == 0.0
    assert result.interpretation == "No direct persona-memory alignment found."


def test_original_memory_data_is_unchanged() -> None:
    fusion = PersonaMemoryFusion()
    persona = make_persona(
        "Architect",
        {"focus": "architecture modular boundaries"},
    )
    memory = make_memory()
    original_state = (
        memory.content,
        memory.category,
        memory.confidence,
        memory.importance,
        memory.source,
        memory.timestamp,
        memory.state,
    )

    fusion.fuse(persona, memory)

    assert (
        memory.content,
        memory.category,
        memory.confidence,
        memory.importance,
        memory.source,
        memory.timestamp,
        memory.state,
    ) == original_state
