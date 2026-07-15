"""Tests for persona activation boundary."""

from backend.core import (
    PersonaActivationManager,
    PersonaLibraryEngine,
    PersonaSelector,
)
from backend.models import (
    PersonaActivationStatus,
    PersonaLibraryEntry,
    PersonaVersion,
)


def make_version(version_id: str = "architect-version-1") -> PersonaVersion:
    return PersonaVersion(
        id=version_id,
        persona_name="Architect",
        version="1.0",
        created_at="2026-07-15",
        profile_snapshot={"name": "Architect", "style": "structured"},
        source_ids=["source-1"],
        change_note="Initial reviewed profile.",
    )


def make_entry(
    *,
    approved: bool = True,
    rejected: bool = False,
    with_version: bool = True,
) -> PersonaLibraryEntry:
    version = make_version()
    entry = PersonaLibraryEntry(
        id="architect",
        name="Architect",
        current_version_id=version.id if with_version else "",
        versions=[version] if with_version else [],
    )
    entry.submit_for_review(reviewer="Morgan")
    if approved:
        entry.approve(reviewer="Morgan")
    if rejected:
        entry.reject(reviewer="Morgan")
    return entry


def test_approved_persona_can_activate() -> None:
    manager = PersonaActivationManager()
    entry = make_entry()

    activation = manager.activate(
        entry,
        activated_by="Morgan",
        activated_at="2026-07-15",
    )

    assert activation is not None
    assert activation.persona_entry_id == "architect"
    assert activation.persona_version_id == "architect-version-1"
    assert activation.activated_by == "Morgan"
    assert activation.activated_at == "2026-07-15"
    assert activation.status == PersonaActivationStatus.ACTIVE
    assert entry.is_selectable() is True
    assert manager.get_active_personas() == [entry]


def test_draft_persona_cannot_activate() -> None:
    manager = PersonaActivationManager()
    version = make_version()
    entry = PersonaLibraryEntry(
        id="architect",
        name="Architect",
        current_version_id=version.id,
        versions=[version],
    )

    activation = manager.activate(entry)

    assert activation is None
    assert entry.activations == []
    assert entry.is_selectable() is False
    assert manager.get_active_personas() == []


def test_rejected_persona_cannot_activate() -> None:
    manager = PersonaActivationManager()
    entry = make_entry(approved=False, rejected=True)

    activation = manager.activate(entry)

    assert activation is None
    assert entry.activations == []
    assert entry.is_selectable() is False
    assert manager.get_active_personas() == []


def test_inactive_persona_cannot_be_selected() -> None:
    manager = PersonaActivationManager()
    entry = make_entry()
    activation = manager.activate(entry)
    library = PersonaLibraryEngine()
    library.add_persona(entry)
    selector = PersonaSelector(library)

    deactivated = manager.deactivate(entry)
    selected = selector.select("architect")

    assert deactivated is activation
    assert selected is None
    assert selector.get_current() is None
    assert activation.status == PersonaActivationStatus.INACTIVE
    assert entry.is_selectable() is False
    assert manager.get_active_personas() == []


def test_activation_requires_valid_version_reference() -> None:
    manager = PersonaActivationManager()
    entry = make_entry(with_version=False)

    activation = manager.activate(entry)

    assert activation is None
    assert entry.is_selectable() is False
    assert manager.get_active_personas() == []


def test_activation_keeps_version_snapshot_unchanged() -> None:
    manager = PersonaActivationManager()
    entry = make_entry()
    snapshot = dict(entry.versions[0].profile_snapshot)

    manager.activate(entry)
    manager.deactivate(entry)

    assert entry.current_version_id == "architect-version-1"
    assert entry.versions[0].profile_snapshot == snapshot
    assert len(entry.activations) == 1
    assert entry.activations[0].status == PersonaActivationStatus.INACTIVE
