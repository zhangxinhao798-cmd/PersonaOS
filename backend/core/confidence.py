"""Confidence Engine skeleton."""

from backend.models.memory_record import MemoryRecord


class ConfidenceEngine:
    """Evaluates reliability awareness across PersonaOS.

    The Confidence Engine should eventually assess evidence, detect
    uncertainty, analyze risk, and calibrate behavior to prevent
    overconfidence.
    """

    def __init__(
        self,
        source_reliability: dict[str, float] | None = None,
    ) -> None:
        self.source_reliability = source_reliability or {
            "system": 0.8,
            "user": 0.7,
            "test": 0.5,
            "unknown": 0.5,
            "inferred": 0.4,
        }
        self._repeated_confirmations: dict[int, int] = {}
        self._uncertainty_penalties: dict[int, float] = {}

    def calculate_confidence(self, memory: MemoryRecord) -> float:
        """Calculate a deterministic confidence score for a memory.

        The score combines the memory's current confidence with source
        reliability, repeated confirmation, evidence strength history, and
        uncertainty penalties. The ConfidenceEngine does not own memory
        storage; it only evaluates a provided MemoryRecord.
        """

        memory_id = id(memory)
        source_score = self.source_reliability.get(
            memory.source,
            self.source_reliability["unknown"],
        )
        source_adjustment = (source_score - 0.5) * 0.2
        confirmation_bonus = min(
            self._repeated_confirmations.get(memory_id, 0) * 0.05,
            0.2,
        )
        uncertainty_penalty = self._uncertainty_penalties.get(memory_id, 0.0)

        confidence = (
            memory.confidence
            + source_adjustment
            + confirmation_bonus
            - uncertainty_penalty
        )
        return self._clamp(confidence)

    def update_confidence(
        self,
        memory: MemoryRecord,
        evidence_strength: float,
    ) -> float:
        """Update a memory confidence score using new evidence.

        Positive evidence increases confidence and records repeated
        confirmation. Negative evidence lowers confidence and adds an
        uncertainty penalty. The final value is always kept between 0.0 and
        1.0.
        """

        memory_id = id(memory)
        bounded_evidence = max(-1.0, min(1.0, evidence_strength))

        if bounded_evidence > 0:
            self._repeated_confirmations[memory_id] = (
                self._repeated_confirmations.get(memory_id, 0) + 1
            )
            self._uncertainty_penalties[memory_id] = 0.0
        elif bounded_evidence < 0:
            self._uncertainty_penalties[memory_id] = abs(
                bounded_evidence
            ) * 0.05

        memory.confidence = self._clamp(
            memory.confidence + (bounded_evidence * 0.2)
        )
        memory.confidence = self.calculate_confidence(memory)
        return memory.confidence

    def evaluate(
        self,
        memories: list[MemoryRecord],
        knowledge_records: list | None = None,
    ) -> dict:
        """Evaluate reliability signals for orchestration context."""

        memory_scores = [
            self.calculate_confidence(memory)
            for memory in memories
        ]
        knowledge_records = knowledge_records or []

        if not memory_scores:
            return {
                "score": 0.0,
                "factors": {
                    "memory_scores": [],
                    "knowledge_record_count": len(knowledge_records),
                },
            }

        return {
            "score": sum(memory_scores) / len(memory_scores),
            "factors": {
                "memory_scores": memory_scores,
                "knowledge_record_count": len(knowledge_records),
            },
        }

    def _clamp(self, value: float) -> float:
        """Clamp a confidence value to the valid confidence range."""

        return max(0.0, min(1.0, value))
