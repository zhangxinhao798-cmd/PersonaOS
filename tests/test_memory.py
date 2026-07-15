"""MemoryEngine tests."""

from backend.core.memory import MemoryEngine
from backend.models.memory_record import MemoryRecord


def test_create_memory_stores_and_returns_memory() -> None:
    """Creating a memory should store and return the same record."""

    engine = MemoryEngine()
    memory = MemoryRecord(
        content="User prefers concise architecture notes.",
        category="semantic",
        confidence=0.9,
        importance=0.8,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )

    created_memory = engine.create_memory(memory)

    assert created_memory is memory
    assert engine.get_memories() == [memory]


def test_get_memories_returns_all_stored_memories() -> None:
    """Retrieving memories should return all records stored so far."""

    engine = MemoryEngine()
    first_memory = MemoryRecord(
        content="First memory.",
        category="episodic",
        confidence=0.7,
        importance=0.6,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )
    second_memory = MemoryRecord(
        content="Second memory.",
        category="working",
        confidence=0.8,
        importance=0.5,
        source="test",
        timestamp="2026-07-15T00:01:00Z",
    )

    engine.create_memory(first_memory)
    engine.create_memory(second_memory)

    assert engine.get_memories() == [first_memory, second_memory]
