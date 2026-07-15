"""MemoryEngine retrieval tests."""

from backend.core.memory import MemoryEngine
from backend.models.memory_record import MemoryRecord


def make_memory(
    content: str,
    category: str,
    confidence: float,
    importance: float,
    source: str,
) -> MemoryRecord:
    """Create a simple memory record for retrieval tests."""

    return MemoryRecord(
        content=content,
        category=category,
        confidence=confidence,
        importance=importance,
        source=source,
        timestamp="2026-07-15T00:00:00Z",
    )


def test_retrieve_memory_returns_all_memories_without_filters() -> None:
    """Retrieval with no filters should return all stored memories."""

    engine = MemoryEngine()
    first_memory = make_memory("First memory.", "working", 0.6, 0.5, "test")
    second_memory = make_memory("Second memory.", "semantic", 0.9, 0.8, "user")

    engine.create_memory(first_memory)
    engine.create_memory(second_memory)

    assert engine.retrieve_memory() == [first_memory, second_memory]


def test_retrieve_memory_filters_by_category() -> None:
    """Retrieval should support filtering by memory category."""

    engine = MemoryEngine()
    working_memory = make_memory("Working memory.", "working", 0.6, 0.5, "test")
    semantic_memory = make_memory("Semantic memory.", "semantic", 0.9, 0.8, "test")

    engine.create_memory(working_memory)
    engine.create_memory(semantic_memory)

    assert engine.retrieve_memory(category="semantic") == [semantic_memory]


def test_retrieve_memory_filters_by_source() -> None:
    """Retrieval should support filtering by memory source."""

    engine = MemoryEngine()
    test_memory = make_memory("Test memory.", "working", 0.6, 0.5, "test")
    user_memory = make_memory("User memory.", "working", 0.8, 0.7, "user")

    engine.create_memory(test_memory)
    engine.create_memory(user_memory)

    assert engine.retrieve_memory(source="user") == [user_memory]


def test_retrieve_memory_filters_by_minimum_confidence() -> None:
    """Retrieval should support filtering by minimum confidence."""

    engine = MemoryEngine()
    low_confidence_memory = make_memory("Low confidence.", "semantic", 0.4, 0.8, "test")
    high_confidence_memory = make_memory("High confidence.", "semantic", 0.9, 0.8, "test")

    engine.create_memory(low_confidence_memory)
    engine.create_memory(high_confidence_memory)

    assert engine.retrieve_memory(minimum_confidence=0.8) == [high_confidence_memory]


def test_retrieve_memory_filters_by_minimum_importance() -> None:
    """Retrieval should support filtering by minimum importance."""

    engine = MemoryEngine()
    low_importance_memory = make_memory("Low importance.", "episodic", 0.8, 0.3, "test")
    high_importance_memory = make_memory("High importance.", "episodic", 0.8, 0.9, "test")

    engine.create_memory(low_importance_memory)
    engine.create_memory(high_importance_memory)

    assert engine.retrieve_memory(minimum_importance=0.8) == [high_importance_memory]


def test_retrieve_memory_uses_and_logic_for_multiple_filters() -> None:
    """Retrieval should combine multiple filters with AND semantics."""

    engine = MemoryEngine()
    matching_memory = make_memory("Matching memory.", "semantic", 0.9, 0.9, "user")
    wrong_category_memory = make_memory("Wrong category.", "working", 0.9, 0.9, "user")
    wrong_source_memory = make_memory("Wrong source.", "semantic", 0.9, 0.9, "test")
    low_confidence_memory = make_memory("Low confidence.", "semantic", 0.4, 0.9, "user")
    low_importance_memory = make_memory("Low importance.", "semantic", 0.9, 0.4, "user")

    engine.create_memory(matching_memory)
    engine.create_memory(wrong_category_memory)
    engine.create_memory(wrong_source_memory)
    engine.create_memory(low_confidence_memory)
    engine.create_memory(low_importance_memory)

    assert engine.retrieve_memory(
        category="semantic",
        source="user",
        minimum_confidence=0.8,
        minimum_importance=0.8,
    ) == [matching_memory]
