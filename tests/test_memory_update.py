"""MemoryEngine update tests."""

from backend.core.memory import MemoryEngine
from backend.models.memory_record import MemoryRecord
from backend.models.memory_state import MemoryState


def make_memory() -> MemoryRecord:
    """Create a simple memory record for update tests."""

    return MemoryRecord(
        content="Original memory.",
        category="working",
        confidence=0.5,
        importance=0.4,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )


def test_update_memory_can_update_confidence() -> None:
    """Memory confidence should update when provided."""

    engine = MemoryEngine()
    memory = make_memory()

    updated_memory = engine.update_memory(memory, confidence=0.9)

    assert updated_memory.confidence == 0.9


def test_update_memory_can_update_importance() -> None:
    """Memory importance should update when provided."""

    engine = MemoryEngine()
    memory = make_memory()

    updated_memory = engine.update_memory(memory, importance=0.8)

    assert updated_memory.importance == 0.8


def test_update_memory_can_update_category() -> None:
    """Memory category should update when provided."""

    engine = MemoryEngine()
    memory = make_memory()

    updated_memory = engine.update_memory(memory, category="semantic")

    assert updated_memory.category == "semantic"


def test_update_memory_can_update_source() -> None:
    """Memory source should update when provided."""

    engine = MemoryEngine()
    memory = make_memory()

    updated_memory = engine.update_memory(memory, source="user")

    assert updated_memory.source == "user"


def test_update_memory_can_update_state() -> None:
    """Memory state should update when provided."""

    engine = MemoryEngine()
    memory = make_memory()

    updated_memory = engine.update_memory(memory, state=MemoryState.ACTIVE)

    assert updated_memory.state == MemoryState.ACTIVE


def test_update_memory_only_changes_provided_fields() -> None:
    """Omitted fields should remain unchanged during memory update."""

    engine = MemoryEngine()
    memory = make_memory()

    updated_memory = engine.update_memory(memory, confidence=0.95)

    assert updated_memory.content == "Original memory."
    assert updated_memory.category == "working"
    assert updated_memory.confidence == 0.95
    assert updated_memory.importance == 0.4
    assert updated_memory.source == "test"
    assert updated_memory.timestamp == "2026-07-15T00:00:00Z"
    assert updated_memory.state == MemoryState.NEW
