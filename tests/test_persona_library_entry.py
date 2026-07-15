"""Tests for PersonaLibraryEntry workflow boundary fields."""

from backend.models import (
    PersonaLibraryEntry,
    PersonaProfile,
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

    assert entry.lifecycle_state == "draft"


def test_persona_library_entry_stores_current_version_reference() -> None:
    version = make_version("version-1")

    entry = PersonaLibraryEntry(
        current_version_id="version-1",
        versions=[version],
    )

    assert entry.current_version_id == "version-1"
    assert entry.versions[0].id == "version-1"
