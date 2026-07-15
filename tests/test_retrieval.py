"""MemoryRetriever tests."""

from backend.core.retrieval import MemoryRetriever
from backend.models.memory_record import MemoryRecord


def make_memory(
    content: str,
    category: str,
    confidence: float = 0.8,
    importance: float = 0.8,
) -> MemoryRecord:
    """Create a simple memory record for retrieval tests."""

    return MemoryRecord(
        content=content,
        category=category,
        confidence=confidence,
        importance=importance,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )


def test_retrieve_returns_relevant_memories() -> None:
    """Retriever should return memories matching query keywords."""

    project_memory = make_memory(
        "User is designing PersonaOS memory architecture.",
        "semantic",
    )
    unrelated_memory = make_memory(
        "The weather was rainy during the walk.",
        "episodic",
    )
    retriever = MemoryRetriever([project_memory, unrelated_memory])

    results = retriever.retrieve("memory architecture")

    assert project_memory in results
    assert unrelated_memory not in results


def test_retrieve_limit_parameter_works() -> None:
    """Retriever should respect the requested result limit."""

    memories = [
        make_memory("Memory architecture design.", "semantic", 0.9, 0.9),
        make_memory("Memory retrieval flow.", "semantic", 0.8, 0.8),
        make_memory("Memory lifecycle state.", "semantic", 0.7, 0.7),
    ]
    retriever = MemoryRetriever(memories)

    results = retriever.retrieve("memory semantic", limit=2)

    assert len(results) == 2


def test_retrieve_does_not_return_irrelevant_memories() -> None:
    """Retriever should exclude memories with no query keyword matches."""

    unrelated_memory = make_memory(
        "A note about cooking dinner.",
        "episodic",
    )
    retriever = MemoryRetriever([unrelated_memory])

    results = retriever.retrieve("persona memory")

    assert results == []
