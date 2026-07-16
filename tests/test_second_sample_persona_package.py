"""Tests for the second sample Strategist persona package."""

from pathlib import Path

from backend.core import PersonaPackageLoader
from backend.models import PersonaLibraryLifecycleState, PersonaReviewStatus
from scripts import chat_persona


STRATEGIST_PACKAGE_PATH = Path("personas") / "strategist"


def test_second_sample_persona_package_files_exist() -> None:
    assert STRATEGIST_PACKAGE_PATH.is_dir()
    assert (STRATEGIST_PACKAGE_PATH / "manifest.json").is_file()
    assert (STRATEGIST_PACKAGE_PATH / "profile.json").is_file()
    assert (STRATEGIST_PACKAGE_PATH / "examples.json").is_file()
    assert (STRATEGIST_PACKAGE_PATH / "sources.json").is_file()
    assert (STRATEGIST_PACKAGE_PATH / "knowledge.json").is_file()


def test_second_sample_persona_package_validates() -> None:
    result = PersonaPackageLoader().validate(STRATEGIST_PACKAGE_PATH)

    assert result.is_valid is True
    assert result.errors == []


def test_second_sample_persona_package_loads() -> None:
    package = PersonaPackageLoader().load(STRATEGIST_PACKAGE_PATH)

    assert package.manifest.package_id == "strategist"
    assert package.manifest.name == "Strategist"
    assert package.manifest.version == "1.0.0"
    assert package.profile is not None
    assert package.profile.name == "Strategist"
    assert package.profile.traits["focus"] == "decision quality"
    assert package.examples
    assert package.sources
    assert package.knowledge


def test_second_sample_persona_package_converts_to_draft_library_entry() -> None:
    loader = PersonaPackageLoader()
    package = loader.load(STRATEGIST_PACKAGE_PATH)

    entry = loader.to_library_entry(
        package,
        created_at="2026-07-16",
        change_note="Imported from sample Strategist package.",
    )

    assert entry.id == "strategist"
    assert entry.name == "Strategist"
    assert entry.lifecycle_state == PersonaLibraryLifecycleState.DRAFT
    assert entry.review_status == PersonaReviewStatus.PENDING_REVIEW
    assert entry.profile is package.profile
    assert entry.current_version_id == "strategist:1.0.0"
    assert entry.has_valid_current_version() is True
    assert entry.source_ids == [
        "personaos-runtime-configuration",
        "personaos-persona-package-boundary",
    ]


def test_second_sample_persona_package_does_not_become_selectable_automatically() -> None:
    loader = PersonaPackageLoader()
    entry = loader.to_library_entry(loader.load(STRATEGIST_PACKAGE_PATH))

    assert entry.is_approved_for_activation() is False
    assert entry.is_active() is False
    assert entry.is_selectable() is False


def test_cli_discovers_multiple_sample_persona_packages() -> None:
    entries = chat_persona.discover_persona_packages(Path("personas"))
    package_ids = [entry.id for entry in entries]

    assert "architect" in package_ids
    assert "strategist" in package_ids


def test_cli_persona_list_shows_multiple_sample_packages() -> None:
    class MinimalSession:
        def turn_count(self) -> int:
            return 0

    entry = chat_persona.prepare_persona_for_cli_runtime(
        Path("personas") / "architect"
    )
    runtime = chat_persona.InteractiveRuntime(
        session=MinimalSession(),
        persona_entry=entry,
        provider_config=chat_persona.ProviderConfig(
            provider="ollama",
            model="qwen3:14b",
            endpoint="http://localhost:11434",
        ),
        personas_dir=Path("personas"),
    )
    output: list[str] = []

    chat_persona.handle_command("/persona list", runtime, output.append)

    assert any("architect  Architect  v1.0.0" in line for line in output)
    assert any("strategist  Strategist  v1.0.0" in line for line in output)
