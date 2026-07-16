"""Memory candidate promotion boundary for PersonaOS."""

from backend.core.memory import MemoryEngine
from backend.models.memory_candidate import MemoryCandidate
from backend.models.memory_record import MemoryRecord


class MemoryPromotionError(Exception):
    """Base error for memory promotion failures."""


class CandidateNotApprovedError(MemoryPromotionError):
    """Raised when a candidate is not approved for promotion."""


class InvalidMemoryCandidateError(MemoryPromotionError):
    """Raised when an approved candidate cannot become a MemoryRecord."""


class MemoryPromotionBoundary:
    """Promote approved memory candidates into MemoryEngine records.

    This is the only boundary that should connect `MemoryCandidate` to
    `MemoryEngine`. RuntimeSession, SessionManager, CandidateExtractor, and
    ReviewQueue must not write durable memory directly.
    """

    CATEGORY_MAP = {
        "user_preference": "semantic",
        "long_term_goal": "semantic",
        "explicit_personal_fact": "semantic",
        "stable_habit": "procedural",
    }

    IMPORTANCE_MAP = {
        "user_preference": 0.8,
        "long_term_goal": 0.85,
        "explicit_personal_fact": 0.75,
        "stable_habit": 0.7,
    }

    def __init__(self, memory_engine: MemoryEngine) -> None:
        if memory_engine is None:
            raise InvalidMemoryCandidateError("MemoryEngine is required.")
        self.memory_engine = memory_engine

    def promote(self, candidate: MemoryCandidate) -> MemoryRecord:
        """Validate, convert, and store one approved memory candidate."""

        memory_record = self.to_memory_record(candidate)
        return self.memory_engine.create_memory(memory_record)

    def to_memory_record(self, candidate: MemoryCandidate) -> MemoryRecord:
        """Convert an approved candidate into a MemoryRecord."""

        self._validate_candidate(candidate)
        return MemoryRecord(
            content=candidate.content.strip(),
            category=self._category(candidate),
            confidence=candidate.confidence,
            importance=self._importance(candidate),
            source=self._source(candidate),
            timestamp=candidate.reviewed_at or candidate.created_at,
        )

    def _validate_candidate(self, candidate: MemoryCandidate) -> None:
        if candidate is None:
            raise InvalidMemoryCandidateError("Memory candidate is required.")
        if candidate.review_status != "approved":
            raise CandidateNotApprovedError(
                "Only approved memory candidates can be promoted."
            )
        if not isinstance(candidate.content, str) or not candidate.content.strip():
            raise InvalidMemoryCandidateError("Candidate content is required.")
        if not isinstance(candidate.confidence, (int, float)):
            raise InvalidMemoryCandidateError("Candidate confidence is required.")
        if candidate.confidence < 0 or candidate.confidence > 1:
            raise InvalidMemoryCandidateError(
                "Candidate confidence must be between 0 and 1."
            )
        importance = self._importance(candidate)
        if importance < 0 or importance > 1:
            raise InvalidMemoryCandidateError(
                "Candidate importance must be between 0 and 1."
            )

    def _category(self, candidate: MemoryCandidate) -> str:
        return (
            candidate.category
            or self.CATEGORY_MAP.get(candidate.candidate_type)
            or "semantic"
        )

    def _importance(self, candidate: MemoryCandidate) -> float:
        if candidate.importance is not None:
            return candidate.importance

        return self.IMPORTANCE_MAP.get(candidate.candidate_type, 0.5)

    def _source(self, candidate: MemoryCandidate) -> str:
        return f"memory_candidate:{candidate.id}"
