"""Runtime memory retrieval boundary for PersonaOS sessions."""

from dataclasses import dataclass

from backend.core.retrieval import MemoryRetriever
from backend.models.context import MemoryContext, PersonaOSContext
from backend.models.memory_record import MemoryRecord


@dataclass
class RetrievedMemory:
    """Memory retrieved for one runtime turn with relevance metadata."""

    memory: MemoryRecord
    relevance_score: float
    rank: int

    def relevance_metadata(self) -> dict:
        """Return JSON-safe relevance metadata."""

        return {
            "rank": self.rank,
            "score": self.relevance_score,
            "source": self.memory.source,
            "category": self.memory.category,
        }


class RuntimeMemoryRetriever:
    """Retrieve relevant memories for the current runtime turn.

    This boundary reads already-prepared MemoryContext records only. It does
    not call MemoryEngine, create memories, summarize chat, or persist data.
    """

    def __init__(self, limit: int = 5) -> None:
        self.limit = limit

    def retrieve_relevant_memories(
        self,
        query: str,
        context: PersonaOSContext,
    ) -> MemoryContext:
        """Return a MemoryContext containing relevant memories only."""

        source_memory_context = getattr(context, "memories", None)
        if source_memory_context is None:
            return MemoryContext()

        source_memories = getattr(source_memory_context, "memories", []) or []
        if not source_memories:
            return MemoryContext()

        retriever = MemoryRetriever(source_memories)
        retrieved = [
            RetrievedMemory(memory=memory, relevance_score=score, rank=index)
            for index, (memory, score) in enumerate(
                retriever.retrieve_with_relevance(query, self.limit),
                start=1,
            )
        ]
        return MemoryContext(
            memories=[item.memory for item in retrieved],
            relevance=[item.relevance_metadata() for item in retrieved],
        )
