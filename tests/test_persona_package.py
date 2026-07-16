"""Tests for Persona Package v1 boundaries."""

import json
from pathlib import Path

import pytest

from backend.core import PersonaPackageError, PersonaPackageLoader
from backend.models import (
    PersonaLibraryEntry,
    PersonaLibraryLifecycleState,
    PersonaPackage,
    PersonaPackageManifest,
    PersonaPackageValidationResult,
    PersonaProfile,
)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def create_package(root: Path) -> None:
    write_json(
        root / "manifest.json",
        {
            "package_id": "architect",
            "name": "Architect",
            "version": "1.0.0",
            "description": "Structured design persona.",
            "metadata": {"author": "PersonaOS"},
        },
    )
    write_json(
        root / "profile.json",
        {
            "name": "Architect",
            "traits": {"style": "structured"},
            "values": ["clarity", "boundaries"],
            "style": "precise",
            "boundaries": ["do not merge engine responsibilities"],
            "thinking_patterns": ["separate data from runtime behavior"],
            "communication_style": ["calm", "direct"],
            "speech_patterns": ["Let's inspect the boundary first."],
            "examples": [
                {
                    "question": "What should we do next?",
                    "answer": "Define the boundary before implementation.",
                }
            ],
        },
    )
    write_json(
        root / "examples.json",
        [
            {
                "input": "How should we change this?",
                "output": "Small, testable steps.",
            }
        ],
    )
    write_json(
        root / "sources.json",
        [
            {
                "id": "source-1",
                "name": "Architect notes",
                "source_type": "user_notes",
                "content": "Architecture first.",
                "metadata": {"language": "en"},
            }
        ],
    )
    write_json(
        root / "knowledge.json",
        {
            "references": ["Architecture Principles"],
        },
    )


def test_persona_package_models_initialize_with_independent_defaults() -> None:
    package_a = PersonaPackage()
    package_b = PersonaPackage()
    package_a.examples.append({"input": "hello"})

    assert isinstance(package_a.manifest, PersonaPackageManifest)
    assert isinstance(
        PersonaPackageValidationResult(), PersonaPackageValidationResult
    )
    assert package_a.examples == [{"input": "hello"}]
    assert package_b.examples == []


def test_loader_validates_missing_manifest(tmp_path: Path) -> None:
    result = PersonaPackageLoader().validate(tmp_path)

    assert result.is_valid is False
    assert result.errors == ["Missing manifest.json"]


def test_loader_validates_required_manifest_fields(tmp_path: Path) -> None:
    write_json(tmp_path / "manifest.json", {"name": "Architect"})

    result = PersonaPackageLoader().validate(tmp_path)

    assert result.is_valid is False
    assert "Manifest missing required field: package_id" in result.errors
    assert "Manifest missing required field: version" in result.errors
    assert "Missing profile file: profile.json" in result.errors


def test_loader_loads_complete_persona_package(tmp_path: Path) -> None:
    create_package(tmp_path)

    package = PersonaPackageLoader().load(tmp_path)

    assert package.manifest.package_id == "architect"
    assert package.manifest.name == "Architect"
    assert package.manifest.version == "1.0.0"
    assert package.manifest.metadata == {"author": "PersonaOS"}
    assert isinstance(package.profile, PersonaProfile)
    assert package.profile.name == "Architect"
    assert package.profile.speech_patterns == [
        "Let's inspect the boundary first."
    ]
    assert package.examples == [
        {
            "input": "How should we change this?",
            "output": "Small, testable steps.",
        }
    ]
    assert package.sources[0].id == "source-1"
    assert package.knowledge == {"references": ["Architecture Principles"]}
    assert package.package_path == str(tmp_path)


def test_loader_optional_files_default_to_empty(tmp_path: Path) -> None:
    write_json(
        tmp_path / "manifest.json",
        {
            "package_id": "minimal",
            "name": "Minimal",
            "version": "1.0.0",
        },
    )
    write_json(
        tmp_path / "profile.json",
        {
            "name": "Minimal",
            "traits": {},
            "values": [],
            "style": "",
            "boundaries": [],
        },
    )

    package = PersonaPackageLoader().load(tmp_path)

    assert package.examples == []
    assert package.sources == []
    assert package.knowledge == {}


def test_loader_rejects_invalid_optional_file_shapes(tmp_path: Path) -> None:
    create_package(tmp_path)
    write_json(tmp_path / "examples.json", {"not": "a list"})

    with pytest.raises(PersonaPackageError):
        PersonaPackageLoader().load(tmp_path)


def test_loader_converts_package_to_draft_library_entry(tmp_path: Path) -> None:
    create_package(tmp_path)
    loader = PersonaPackageLoader()
    package = loader.load(tmp_path)

    entry = loader.to_library_entry(
        package,
        created_at="2026-07-16",
        change_note="Imported from persona package.",
    )

    assert isinstance(entry, PersonaLibraryEntry)
    assert entry.id == "architect"
    assert entry.name == "Architect"
    assert entry.description == "Structured design persona."
    assert entry.lifecycle_state == PersonaLibraryLifecycleState.DRAFT
    assert entry.review_status == "pending_review"
    assert entry.is_selectable() is False
    assert entry.profile is package.profile
    assert entry.current_version_id == "architect:1.0.0"
    assert entry.source_ids == ["source-1"]
    assert len(entry.versions) == 1
    assert entry.versions[0].id == "architect:1.0.0"
    assert entry.versions[0].created_at == "2026-07-16"
    assert entry.versions[0].profile_snapshot["name"] == "Architect"
    assert entry.versions[0].profile_snapshot["speech_patterns"] == [
        "Let's inspect the boundary first."
    ]


def test_loader_conversion_requires_profile() -> None:
    package = PersonaPackage(
        manifest=PersonaPackageManifest(
            package_id="broken",
            name="Broken",
            version="1.0.0",
        )
    )

    with pytest.raises(PersonaPackageError):
        PersonaPackageLoader().to_library_entry(package)

