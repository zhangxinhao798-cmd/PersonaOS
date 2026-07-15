"""Memory Engine skeleton."""

from backend.models.memory_record import MemoryRecord


class MemoryEngine:
    """Manages experience-derived continuity for a digital mind.

    The Memory Engine is responsible for future memory creation, retrieval,
    update, consolidation, and forgetting. It should stay separate from
    raw conversation history and external knowledge.
    """

    def __init__(self) -> None:
        self._memories: list[MemoryRecord] = []

    def create_memory(self, memory: MemoryRecord) -> MemoryRecord:
        """Store a persistent memory and return it."""

        self._memories.append(memory)
        return memory

    def get_memories(self) -> list[MemoryRecord]:
        """Return all stored memories."""

        return self._memories
