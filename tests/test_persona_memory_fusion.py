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


def test_same_memory_different_personas_produce_different_interpretations() -> None:
    fusion = PersonaMemoryFusion()
    memory = MemoryRecord(
        content="user investment loss",
        category="episodic",
        confidence=0.8,
        importance=0.9,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )
    investment_persona = make_persona(
        "Value Investor",
        {"focus": "investment value loss"},
    )
    reflection_persona = make_persona(
        "Reflective Coach",
        {"focus": "self reflection loss"},
    )

    investment_result = fusion.fuse(investment_persona, memory)
    reflection_result = fusion.fuse(reflection_persona, memory)

    assert investment_result != reflection_result
    assert investment_result.interpretation != reflection_result.interpretation


def test_persona_relevance_affects_scoring() -> None:
    fusion = PersonaMemoryFusion()
    memory = MemoryRecord(
        content="user investment loss",
        category="episodic",
        confidence=0.8,
        importance=0.9,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )
    related_persona = make_persona(
        "Value Investor",
        {"focus": "investment loss value"},
    )
    unrelated_persona = make_persona(
        "Gardener",
        {"focus": "plants soil watering"},
    )

    related_result = fusion.fuse(related_persona, memory)
    unrelated_result = fusion.fuse(unrelated_persona, memory)

    assert related_result.relevance_score > unrelated_result.relevance_score
