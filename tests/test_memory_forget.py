"""MemoryEngine forget tests."""

from backend.core.memory import MemoryEngine
from backend.models.memory_record import MemoryRecord
from backend.models.memory_state import MemoryState


def make_memory() -> MemoryRecord:
    """Create a simple memory record for forget tests."""

    return MemoryRecord(
        content="Memory to forget.",
        category="episodic",
        confidence=0.8,
        importance=0.7,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )


def test_forget_memory_changes_state_to_forgotten() -> None:
    """Forgetting a memory should mark its state as forgotten."""

    engine = MemoryEngine()
    memory = make_memory()

    forgotten_memory = engine.forget_memory(memory)

    assert forgotten_memory.state == MemoryState.FORGOTTEN


def test_forget_memory_does_not_delete_memory_record() -> None:
    """Forgetting a memory should not remove it from stored records."""

    engine = MemoryEngine()
    memory = make_memory()
    engine.create_memory(memory)

    engine.forget_memory(memory)

    assert engine.get_memories() == [memory]


def test_forget_memory_returns_same_object() -> None:
    """Forgetting a memory should return the same memory object."""

    engine = MemoryEngine()
    memory = make_memory()

    forgotten_memory = engine.forget_memory(memory)

    assert forgotten_memory is memory
