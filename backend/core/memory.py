"""Memory Engine skeleton."""

from backend.core.persona import PersonaEngine
from backend.models.memory_record import MemoryRecord
from backend.models.memory_state import MemoryState


class MemoryEngine:
    """Manages experience-derived continuity for a digital mind.

    The Memory Engine is responsible for future memory creation, retrieval,
    update, consolidation, and forgetting. It should stay separate from
    raw conversation history and external knowledge.
    """

    def __init__(self, persona_engine: PersonaEngine | None = None) -> None:
        self._memories: list[MemoryRecord] = []
        self._persona_engine = persona_engine

    def set_persona_engine(self, persona_engine: PersonaEngine) -> PersonaEngine:
        """Set the active persona engine used for memory preferences."""

        self._persona_engine = persona_engine
        return persona_engine

    def get_persona_engine(self) -> PersonaEngine | None:
        """Return the active persona engine, if one has been configured."""

        return self._persona_engine

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

    def calculate_memory_priority(self, memory: MemoryRecord) -> float:
        """Calculate deterministic memory priority from memory and persona.

        The base score uses memory importance and confidence. If an active
        persona provides memory preferences, category and keyword matches add
        small deterministic boosts. Future versions can replace this with more
        nuanced ranking while preserving the Persona/Memory boundary.
        """

        priority = memory.importance + memory.confidence

        if self._persona_engine is None:
            return priority

        preferences = self._persona_engine.get_memory_preferences()
        preferred_categories = preferences["preferred_categories"]
        priority_keywords = preferences["priority_keywords"]

        if memory.category.lower() in preferred_categories:
            priority += 1.0

        searchable_text = f"{memory.content} {memory.category}".lower()
        for keyword in priority_keywords:
            if keyword in searchable_text:
                priority += 0.5

        return priority
