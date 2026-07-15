"""Memory Engine skeleton."""

from backend.models.memory_record import MemoryRecord
from backend.models.memory_state import MemoryState


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

    def retrieve_memory(
        self,
        category: str | None = None,
        source: str | None = None,
        minimum_confidence: float | None = None,
        minimum_importance: float | None = None,
    ) -> list[MemoryRecord]:
        """Return memories matching the provided optional filters.

        Filters are combined with AND semantics. When no filters are provided,
        all stored memories are returned.
        """

        memories = self._memories

        if category is not None:
            memories = [
                memory for memory in memories if memory.category == category
            ]

        if source is not None:
            memories = [memory for memory in memories if memory.source == source]

        if minimum_confidence is not None:
            memories = [
                memory
                for memory in memories
                if memory.confidence >= minimum_confidence
            ]

        if minimum_importance is not None:
            memories = [
                memory
                for memory in memories
                if memory.importance >= minimum_importance
            ]

        return memories

    def update_memory(
        self,
        memory: MemoryRecord,
        confidence: float | None = None,
        importance: float | None = None,
        category: str | None = None,
        source: str | None = None,
        state: MemoryState | None = None,
    ) -> MemoryRecord:
        """Update provided lifecycle fields on a memory record.

        Only values passed explicitly are applied. Existing values are
        preserved when an argument is omitted.
        """

        if confidence is not None:
            memory.confidence = confidence

        if importance is not None:
            memory.importance = importance

        if category is not None:
            memory.category = category

        if source is not None:
            memory.source = source

        if state is not None:
            memory.state = state

        return memory

    def forget_memory(self, memory: MemoryRecord) -> MemoryRecord:
        """Mark a memory as forgotten without deleting the record."""

        memory.state = MemoryState.FORGOTTEN
        return memory
