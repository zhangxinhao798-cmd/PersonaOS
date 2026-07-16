"""Reviewable memory candidate models for PersonaOS."""

from dataclasses import dataclass, field


@dataclass
class MemoryCandidate:
    """A reviewable candidate between conversation and durable memory.

    A candidate is not a durable memory. Approval marks it as ready for a
    future human-controlled promotion path, but this model does not write to
    MemoryEngine or any repository.
    """

    id: str
    source_turn: dict
    candidate_type: str
    content: str
    confidence: float
    reason: str
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    review_status: str = "pending"
    reviewed_at: str = ""
    review_reason: str = ""

    def __post_init__(self) -> None:
        self.source_turn = dict(self.source_turn or {})
        self.metadata = dict(self.metadata or {})

    def approve(self, reason: str = "", reviewed_at: str = "") -> None:
        """Mark the candidate approved without creating durable memory."""

        self.review_status = "approved"
        self.review_reason = reason
        self.reviewed_at = reviewed_at

    def reject(self, reason: str = "", reviewed_at: str = "") -> None:
        """Mark the candidate rejected without creating durable memory."""

        self.review_status = "rejected"
        self.review_reason = reason
        self.reviewed_at = reviewed_at

    def to_dict(self) -> dict:
        """Return an API-safe candidate mapping."""

        return {
            "id": self.id,
            "source_turn": dict(self.source_turn),
            "candidate_type": self.candidate_type,
            "content": self.content,
            "confidence": self.confidence,
            "reason": self.reason,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "review_status": self.review_status,
            "reviewed_at": self.reviewed_at,
            "review_reason": self.review_reason,
        }
