"""PersonaOS memory retrieval integration tests."""

from backend.core.memory import MemoryEngine
from backend.core.retrieval import MemoryRetriever
from backend.engine.persona_os import PersonaOS
from backend.models.memory_record import MemoryRecord


def make_memory(content: str, category: str) -> MemoryRecord:
    """Create a simple memory record for PersonaOS integration tests."""

    return MemoryRecord(
        content=content,
        category=category,
        confidence=0.8,
        importance=0.8,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )


def test_persona_os_memory_system_retrieves_relevant_memories() -> None:
    """PersonaOS memory records should be retrievable by relevance."""

    persona_os = PersonaOS()

    assert isinstance(persona_os.memory_engine, MemoryEngine)

    relevant_memory = make_memory(
        "PersonaOS should remember architecture decisions.",
        "semantic",
    )
    unrelated_memory = make_memory(
        "A note about preparing lunch.",
        "episodic",
    )

    persona_os.memory_engine.create_memory(relevant_memory)
    persona_os.memory_engine.create_memory(unrelated_memory)

    retriever = MemoryRetriever(persona_os.memory_engine.get_memories())
    results = retriever.retrieve("architecture memory")

    assert relevant_memory in results
    assert unrelated_memory not in results
