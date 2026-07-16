"""Memory candidate review controls boundary for PersonaOS."""

from backend.core.memory_candidate import (
    MemoryCandidateNotFoundError,
    ReviewQueue,
)
from backend.core.memory_promotion import MemoryPromotionBoundary
from backend.models.memory_candidate import MemoryCandidate
from backend.models.memory_record import MemoryRecord


class MemoryReviewApiError(Exception):
    """Base error for memory review API failures."""


class MemoryReviewValidationError(MemoryReviewApiError):
    """Raised when a memory review request is invalid."""


class MemoryReviewApiBoundary:
    """Controlled review boundary for memory candidates.

    This boundary exposes explicit review controls without allowing runtime,
    sessions, or transports to write durable memories directly.
    """

    def __init__(
        self,
        review_queue: ReviewQueue,
        promotion_boundary: MemoryPromotionBoundary | None = None,
    ) -> None:
        if review_queue is None:
            raise MemoryReviewValidationError("ReviewQueue is required.")

        self.review_queue = review_queue
        self.promotion_boundary = promotion_boundary

    def list_candidates(
        self,
        status: str | None = None,
    ) -> list[MemoryCandidate]:
        """List queued candidates, optionally filtered by review status."""

        if status is not None and status not in {"pending", "approved", "rejected"}:
            raise MemoryReviewValidationError(
                "status must be pending, approved, or rejected."
            )

        return self.review_queue.list_candidates(status=status)

    def approve_candidate(
        self,
        candidate_id: str,
        reason: str = "",
        reviewed_at: str = "",
    ) -> MemoryCandidate:
        """Approve one candidate without promoting it."""

        self._validate_candidate_id(candidate_id)
        return self.review_queue.approve(
            candidate_id,
            reason=reason,
            reviewed_at=reviewed_at,
        )

    def reject_candidate(
        self,
        candidate_id: str,
        reason: str = "",
        reviewed_at: str = "",
    ) -> MemoryCandidate:
        """Reject one candidate without promoting it."""

        self._validate_candidate_id(candidate_id)
        return self.review_queue.reject(
            candidate_id,
            reason=reason,
            reviewed_at=reviewed_at,
        )

    def promote_candidate(self, candidate_id: str) -> MemoryRecord:
        """Promote one approved candidate through the promotion boundary."""

        self._validate_candidate_id(candidate_id)
        if self.promotion_boundary is None:
            raise MemoryReviewValidationError(
                "Memory promotion boundary is required."
            )

        candidate = self.review_queue.get(candidate_id)
        return self.promotion_boundary.promote(candidate)

    def clear_candidates(self) -> None:
        """Clear only the temporary review queue."""

        self.review_queue.clear()

    def _validate_candidate_id(self, candidate_id: str) -> None:
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise MemoryReviewValidationError("candidate_id is required.")


__all__ = [
    "MemoryCandidateNotFoundError",
    "MemoryReviewApiBoundary",
    "MemoryReviewApiError",
    "MemoryReviewValidationError",
]
