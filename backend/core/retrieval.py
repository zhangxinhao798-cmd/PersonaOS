"""Memory retrieval helpers for PersonaOS."""

from backend.models.memory_record import MemoryRecord


class MemoryRetriever:
    """Retrieves relevant memories from a provided memory list."""

    def __init__(self, memories: list[MemoryRecord]) -> None:
        self.memories = memories

    def retrieve(self, query: str, limit: int = 5) -> list[MemoryRecord]:
        """Return the most relevant memories for a query.

        This first version uses simple keyword matching against memory content
        and category, then adjusts relevance with importance and confidence.
        Future versions should support semantic search, recency weighting,
        state filtering, source reliability, and persona-specific retrieval.
        """

        return [
            memory
            for memory, _score in self.retrieve_with_relevance(query, limit)
        ]

    def retrieve_with_relevance(
        self,
        query: str,
        limit: int = 5,
    ) -> list[tuple[MemoryRecord, float]]:
        """Return relevant memories with deterministic relevance scores."""

        query_words = self._tokenize(query)
        if not query_words or limit <= 0:
            return []

        scored_memories = [
            (memory, self._score_memory(memory, query_words))
            for memory in self.memories
        ]
        relevant_memories = [
            (memory, score)
            for memory, score in scored_memories
            if score > 0
        ]

        relevant_memories.sort(key=lambda item: item[1], reverse=True)

        return relevant_memories[:limit]

    def _score_memory(self, memory: MemoryRecord, query_words: set[str]) -> float:
        """Score a memory using keyword matches and memory weights."""

        searchable_words = self._tokenize(
            f"{memory.content} {memory.category}"
        )
        keyword_matches = len(query_words & searchable_words)

        if keyword_matches == 0:
            return 0.0

        # Importance and confidence are lightweight relevance multipliers for
        # now. Future ranking can replace this with richer retrieval signals.
        return keyword_matches * (1 + memory.importance + memory.confidence)

    def _tokenize(self, text: str) -> set[str]:
        """Split text into lowercase keyword tokens."""

        return {
            word.strip(".,!?;:()[]{}\"'")
            for word in text.lower().split()
            if word.strip(".,!?;:()[]{}\"'")
        }
