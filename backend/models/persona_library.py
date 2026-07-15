"""Persona library boundary models for PersonaOS."""

from dataclasses import dataclass, field
from enum import Enum

from backend.models.persona_profile import PersonaProfile
from backend.models.persona_version import PersonaVersion


class PersonaLibraryLifecycleState(str, Enum):
    """Lifecycle states for persona library records."""

    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    ARCHIVED = "archived"


ALLOWED_LIFECYCLE_TRANSITIONS = {
    PersonaLibraryLifecycleState.DRAFT: {
        PersonaLibraryLifecycleState.REVIEWING,
    },
    PersonaLibraryLifecycleState.REVIEWING: {
        PersonaLibraryLifecycleState.APPROVED,
        PersonaLibraryLifecycleState.DRAFT,
    },
    PersonaLibraryLifecycleState.APPROVED: {
        PersonaLibraryLifecycleState.ARCHIVED,
    },
    PersonaLibraryLifecycleState.ARCHIVED: set(),
}


class PersonaReviewStatus(str, Enum):
    """Review status values for persona library entries."""

    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class PersonaReview:
    """Human review record for a persona library entry."""

    review_id: str = field(default_factory=str)
    persona_entry_id: str = field(default_factory=str)
    reviewer: str = field(default_factory=str)
    status: PersonaReviewStatus = PersonaReviewStatus.PENDING_REVIEW
    notes: str = field(default_factory=str)
    created_at: str = field(default_factory=str)

    def __post_init__(self) -> None:
        self.status = PersonaReviewStatus(self.status)


@dataclass
class PersonaSource:
    """Source metadata for a persona library entry."""

    source_type: str = field(default_factory=str)
    title: str = field(default_factory=str)
    description: str = field(default_factory=str)


@dataclass
class PersonaKnowledge:
    """Structured knowledge attached to a persona library entry."""

    beliefs: list[str] = field(default_factory=list)
    principles: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


@dataclass
class PersonaLibraryEntry:
    """Stored persona library entry data boundary."""

    id: str = field(default_factory=str)
    name: str = field(default_factory=str)
    description: str = field(default_factory=str)
    lifecycle_state: PersonaLibraryLifecycleState = (
        PersonaLibraryLifecycleState.DRAFT
    )
    review_status: PersonaReviewStatus = PersonaReviewStatus.PENDING_REVIEW
    current_version_id: str = field(default_factory=str)
    profile: PersonaProfile | None = None
    versions: list[PersonaVersion] = field(default_factory=list)
    reviews: list[PersonaReview] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    source: PersonaSource = field(default_factory=PersonaSource)
    traits: list[str] = field(default_factory=list)
    knowledge: PersonaKnowledge = field(default_factory=PersonaKnowledge)

    def __post_init__(self) -> None:
        self.lifecycle_state = PersonaLibraryLifecycleState(
            self.lifecycle_state
        )
        self.review_status = PersonaReviewStatus(self.review_status)

    def can_transition_to(
        self,
        lifecycle_state: PersonaLibraryLifecycleState | str,
    ) -> bool:
        """Return whether the entry can move to the requested state."""

        target_state = PersonaLibraryLifecycleState(lifecycle_state)
        allowed_states = ALLOWED_LIFECYCLE_TRANSITIONS[self.lifecycle_state]
        return target_state in allowed_states

    def transition_to(
        self,
        lifecycle_state: PersonaLibraryLifecycleState | str,
    ) -> bool:
        """Move to a valid lifecycle state and reject invalid transitions."""

        target_state = PersonaLibraryLifecycleState(lifecycle_state)
        if not self.can_transition_to(target_state):
            return False

        self.lifecycle_state = target_state
        return True

    def submit_for_review(
        self,
        reviewer: str = "",
        notes: str = "",
        review_id: str = "",
        created_at: str = "",
    ) -> PersonaReview:
        """Create a pending review record and mark the entry as reviewing."""

        if self.lifecycle_state == PersonaLibraryLifecycleState.DRAFT:
            self.transition_to(PersonaLibraryLifecycleState.REVIEWING)

        review = self._create_review(
            status=PersonaReviewStatus.PENDING_REVIEW,
            reviewer=reviewer,
            notes=notes,
            review_id=review_id,
            created_at=created_at,
        )
        self.review_status = PersonaReviewStatus.PENDING_REVIEW
        return review

    def approve(
        self,
        reviewer: str = "",
        notes: str = "",
        review_id: str = "",
        created_at: str = "",
    ) -> PersonaReview:
        """Approve review availability without modifying version history."""

        if self.lifecycle_state == PersonaLibraryLifecycleState.DRAFT:
            self.transition_to(PersonaLibraryLifecycleState.REVIEWING)

        self.transition_to(PersonaLibraryLifecycleState.APPROVED)
        review = self._create_review(
            status=PersonaReviewStatus.APPROVED,
            reviewer=reviewer,
            notes=notes,
            review_id=review_id,
            created_at=created_at,
        )
        self.review_status = PersonaReviewStatus.APPROVED
        return review

    def reject(
        self,
        reviewer: str = "",
        notes: str = "",
        review_id: str = "",
        created_at: str = "",
    ) -> PersonaReview:
        """Reject review availability without modifying version history."""

        if self.lifecycle_state == PersonaLibraryLifecycleState.DRAFT:
            self.transition_to(PersonaLibraryLifecycleState.REVIEWING)

        review = self._create_review(
            status=PersonaReviewStatus.REJECTED,
            reviewer=reviewer,
            notes=notes,
            review_id=review_id,
            created_at=created_at,
        )
        self.review_status = PersonaReviewStatus.REJECTED
        return review

    def is_selectable(self) -> bool:
        """Return whether the entry is approved for persona selection."""

        return (
            self.lifecycle_state == PersonaLibraryLifecycleState.APPROVED
            and self.review_status == PersonaReviewStatus.APPROVED
        )

    def _create_review(
        self,
        status: PersonaReviewStatus,
        reviewer: str,
        notes: str,
        review_id: str,
        created_at: str,
    ) -> PersonaReview:
        review = PersonaReview(
            review_id=review_id or self._next_review_id(),
            persona_entry_id=self.id,
            reviewer=reviewer,
            status=status,
            notes=notes,
            created_at=created_at,
        )
        self.reviews.append(review)
        return review

    def _next_review_id(self) -> str:
        entry_id = self.id or "persona-entry"
        return f"{entry_id}-review-{len(self.reviews) + 1}"
