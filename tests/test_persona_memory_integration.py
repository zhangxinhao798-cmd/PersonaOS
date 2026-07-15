"""Persona-Memory integration tests."""

from backend.core.memory import MemoryEngine
from backend.core.persona import PersonaEngine
from backend.models.memory_record import MemoryRecord


def make_memory(
    content: str,
    category: str,
    confidence: float = 0.5,
    importance: float = 0.5,
) -> MemoryRecord:
    """Create a simple memory record for integration tests."""

    return MemoryRecord(
        content=content,
        category=category,
        confidence=confidence,
        importance=importance,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )


def test_persona_engine_provides_memory_preferences() -> None:
    """PersonaEngine should expose memory preferences from traits."""

    persona = PersonaEngine()
    persona.set_trait("memory_category", "semantic, episodic")
    persona.set_trait("memory_keywords", "architecture, continuity")

    preferences = persona.get_memory_preferences()

    assert preferences["preferred_categories"] == ["semantic", "episodic"]
    assert preferences["priority_keywords"] == ["architecture", "continuity"]


def test_memory_engine_can_access_active_persona() -> None:
    """MemoryEngine should store and expose its active persona engine."""

    persona = PersonaEngine()
    memory_engine = MemoryEngine(persona)

    assert memory_engine.get_persona_engine() is persona


def test_memory_priority_uses_base_importance_and_confidence() -> None:
    """Memory priority should use memory scores without persona preferences."""

    memory = make_memory(
        "General memory.",
        "working",
        confidence=0.7,
        importance=0.4,
    )
    memory_engine = MemoryEngine()

    assert memory_engine.calculate_memory_priority(memory) == 1.1


def test_memory_priority_is_influenced_by_persona_traits() -> None:
    """Persona traits should increase priority for matching memories."""

    persona = PersonaEngine()
    persona.set_trait("memory_category", "semantic")
    persona.set_trait("memory_keywords", "architecture")
    memory_engine = MemoryEngine(persona)
    matching_memory = make_memory(
        "Architecture decision for PersonaOS.",
        "semantic",
        confidence=0.5,
        importance=0.5,
    )
    non_matching_memory = make_memory(
        "Lunch note.",
        "episodic",
        confidence=0.5,
        importance=0.5,
    )

    matching_priority = memory_engine.calculate_memory_priority(
        matching_memory
    )
    non_matching_priority = memory_engine.calculate_memory_priority(
        non_matching_memory
    )

    assert matching_priority > non_matching_priority
