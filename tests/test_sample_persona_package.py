"""Tests for the sample Architect persona package."""

from pathlib import Path

from backend.core import PersonaPackageLoader
from backend.models import PersonaLibraryLifecycleState, PersonaReviewStatus


SAMPLE_PACKAGE_PATH = Path("personas") / "architect"


def test_sample_persona_package_files_exist() -> None:
    assert SAMPLE_PACKAGE_PATH.is_dir()
    assert (SAMPLE_PACKAGE_PATH / "manifest.json").is_file()
    assert (SAMPLE_PACKAGE_PATH / "profile.json").is_file()
    assert (SAMPLE_PACKAGE_PATH / "examples.json").is_file()
    assert (SAMPLE_PACKAGE_PATH / "sources.json").is_file()
    assert (SAMPLE_PACKAGE_PATH / "knowledge.json").is_file()


def test_sample_persona_package_validates() -> None:
    result = PersonaPackageLoader().validate(SAMPLE_PACKAGE_PATH)

    assert result.is_valid is True
    assert result.errors == []


def test_sample_persona_package_loads() -> None:
    package = PersonaPackageLoader().load(SAMPLE_PACKAGE_PATH)

    assert package.manifest.package_id == "architect"
    assert package.manifest.name == "Architect"
    assert package.manifest.version == "1.0.0"
    assert package.profile is not None
    assert package.profile.name == "Architect"
    assert package.examples
    assert package.sources
    assert package.knowledge


def test_sample_persona_package_converts_to_draft_library_entry() -> None:
    loader = PersonaPackageLoader()
    package = loader.load(SAMPLE_PACKAGE_PATH)

    entry = loader.to_library_entry(
        package,
        created_at="2026-07-16",
        change_note="Imported from sample Architect package.",
    )

    assert entry.id == "architect"
    assert entry.name == "Architect"
    assert entry.lifecycle_state == PersonaLibraryLifecycleState.DRAFT
    assert entry.review_status == PersonaReviewStatus.PENDING_REVIEW
    assert entry.profile is package.profile
    assert entry.current_version_id == "architect:1.0.0"
    assert entry.has_valid_current_version() is True
    assert entry.source_ids == [
        "personaos-architecture-principles",
        "personaos-runtime-architecture",
    ]


def test_sample_persona_package_does_not_become_selectable_automatically() -> None:
    loader = PersonaPackageLoader()
    entry = loader.to_library_entry(loader.load(SAMPLE_PACKAGE_PATH))

    assert entry.is_approved_for_activation() is False
    assert entry.is_active() is False
    assert entry.is_selectable() is False
