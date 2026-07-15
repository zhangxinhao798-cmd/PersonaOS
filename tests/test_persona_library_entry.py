"""Tests for PersonaLibraryEntry workflow boundary fields."""

from backend.models import (
    PersonaLibraryEntry,
    PersonaLibraryLifecycleState,
    PersonaProfile,
    PersonaReviewStatus,
    PersonaVersion,
)


def make_profile() -> PersonaProfile:
    return PersonaProfile(
        name="Architect",
        traits={"style": "structured"},
        values=["clarity"],
        style="precise",
        boundaries=["do not merge engine responsibilities"],
    )


def make_version(version_id: str) -> PersonaVersion:
    return PersonaVersion(
        id=version_id,
        persona_name="Architect",
        version="1.0",
        created_at="2026-07-15",
        profile_snapshot={"name": "Architect"},
        source_ids=["source-1"],
        change_note="Initial reviewed profile.",
    )


def test_persona_library_entry_initializes_with_profile_and_sources() -> None:
    profile = make_profile()
    version = make_version("version-1")

    entry = PersonaLibraryEntry(
        id="architect",
        name="Architect",
        description="Structured design persona.",
        profile=profile,
        versions=[version],
        source_ids=["source-1"],
    )

    assert entry.id == "architect"
    assert entry.name == "Architect"
    assert entry.description == "Structured design persona."
    assert entry.profile is profile
    assert entry.versions == [version]
    assert entry.source_ids == ["source-1"]


def test_persona_library_entry_lifecycle_state_defaults_to_draft() -> None:
    entry = PersonaLibraryEntry()

    assert entry.lifecycle_state == PersonaLibraryLifecycleState.DRAFT
    assert entry.lifecycle_state == "draft"


def test_persona_library_entry_stores_current_version_reference() -> None:
    version = make_version("version-1")

    entry = PersonaLibraryEntry(
        current_version_id="version-1",
        versions=[version],
    )

    assert entry.current_version_id == "version-1"
    assert entry.versions[0].id == "version-1"


def test_persona_library_entry_accepts_valid_lifecycle_transitions() -> None:
    entry = PersonaLibraryEntry()

    assert entry.transition_to(PersonaLibraryLifecycleState.REVIEWING) is True
    assert entry.lifecycle_state == PersonaLibraryLifecycleState.REVIEWING

    assert entry.transition_to(PersonaLibraryLifecycleState.APPROVED) is True
    assert entry.lifecycle_state == PersonaLibraryLifecycleState.APPROVED

    assert entry.transition_to(PersonaLibraryLifecycleState.ARCHIVED) is True
    assert entry.lifecycle_state == PersonaLibraryLifecycleState.ARCHIVED


def test_persona_library_entry_can_return_from_reviewing_to_draft() -> None:
    entry = PersonaLibraryEntry(
        lifecycle_state=PersonaLibraryLifecycleState.REVIEWING
    )

    assert entry.transition_to(PersonaLibraryLifecycleState.DRAFT) is True

    assert entry.lifecycle_state == PersonaLibraryLifecycleState.DRAFT


def test_persona_library_entry_rejects_invalid_lifecycle_transitions() -> None:
    entry = PersonaLibraryEntry()

    assert entry.transition_to(PersonaLibraryLifecycleState.APPROVED) is False

    assert entry.lifecycle_state == PersonaLibraryLifecycleState.DRAFT


def test_persona_library_entry_archived_state_rejects_transitions() -> None:
    entry = PersonaLibraryEntry(
        lifecycle_state=PersonaLibraryLifecycleState.APPROVED
    )

    assert entry.transition_to(PersonaLibraryLifecycleState.ARCHIVED) is True
    assert entry.transition_to(PersonaLibraryLifecycleState.REVIEWING) is False
    assert entry.transition_to(PersonaLibraryLifecycleState.DRAFT) is False

    assert entry.lifecycle_state == PersonaLibraryLifecycleState.ARCHIVED


def test_persona_library_entry_lifecycle_does_not_mutate_versions() -> None:
    version = make_version("version-1")
    snapshot = dict(version.profile_snapshot)
    entry = PersonaLibraryEntry(
        lifecycle_state=PersonaLibraryLifecycleState.REVIEWING,
        versions=[version],
    )

    assert entry.transition_to(PersonaLibraryLifecycleState.APPROVED) is True

    assert entry.versions == [version]
    assert entry.versions[0].profile_snapshot == snapshot


def test_persona_library_entry_submit_for_review_creates_review_record() -> None:
    entry = PersonaLibraryEntry(id="architect")

    review = entry.submit_for_review(
        reviewer="Morgan",
        notes="Ready for review.",
        created_at="2026-07-15",
    )

    assert review.persona_entry_id == "architect"
    assert review.reviewer == "Morgan"
    assert review.status == PersonaReviewStatus.PENDING_REVIEW
    assert review.notes == "Ready for review."
    assert review.created_at == "2026-07-15"
    assert entry.reviews == [review]
    assert entry.lifecycle_state == PersonaLibraryLifecycleState.REVIEWING
    assert entry.is_selectable() is False


def test_persona_library_entry_approve_changes_availability() -> None:
    entry = PersonaLibraryEntry(id="architect")
    entry.submit_for_review(reviewer="Morgan")

    review = entry.approve(
        reviewer="Morgan",
        notes="Approved for use.",
    )

    assert review.status == PersonaReviewStatus.APPROVED
    assert entry.review_status == PersonaReviewStatus.APPROVED
    assert entry.lifecycle_state == PersonaLibraryLifecycleState.APPROVED
    assert entry.is_approved_for_activation() is True
    assert entry.is_selectable() is False


def test_persona_library_entry_reject_blocks_selection() -> None:
    entry = PersonaLibraryEntry(id="architect")
    entry.submit_for_review(reviewer="Morgan")

    review = entry.reject(
        reviewer="Morgan",
        notes="Needs revision.",
    )

    assert review.status == PersonaReviewStatus.REJECTED
    assert entry.review_status == PersonaReviewStatus.REJECTED
    assert entry.is_selectable() is False


def test_persona_library_entry_review_does_not_mutate_version_snapshot() -> None:
    version = make_version("version-1")
    snapshot = dict(version.profile_snapshot)
    entry = PersonaLibraryEntry(
        id="architect",
        versions=[version],
        current_version_id="version-1",
    )

    entry.submit_for_review(reviewer="Morgan")
    entry.approve(reviewer="Morgan")

    assert entry.current_version_id == "version-1"
    assert entry.versions == [version]
    assert entry.versions[0].profile_snapshot == snapshot
