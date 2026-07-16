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


def test_retrieve_with_relevance_returns_scores() -> None:
    """Retriever should expose relevance scores for runtime context metadata."""

    high_value_memory = make_memory(
        "User prefers memory runtime architecture.",
        "semantic",
        confidence=0.9,
        importance=0.9,
    )
    lower_value_memory = make_memory(
        "Runtime retrieval keeps session history separate.",
        "semantic",
        confidence=0.5,
        importance=0.4,
    )
    retriever = MemoryRetriever([lower_value_memory, high_value_memory])

    results = retriever.retrieve_with_relevance("memory runtime")

    assert results[0][0] is high_value_memory
    assert results[0][1] > results[1][1]
    assert all(score > 0 for _memory, score in results)


def test_retrieve_with_relevance_handles_empty_query() -> None:
    """Empty queries should not produce runtime memory candidates."""

    retriever = MemoryRetriever([make_memory("Memory architecture.", "semantic")])

    assert retriever.retrieve_with_relevance("   ") == []
