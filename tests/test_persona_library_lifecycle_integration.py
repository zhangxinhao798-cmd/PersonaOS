"""End-to-end Persona Library lifecycle integration tests."""

from backend.core import (
    PersonaActivationManager,
    PersonaImporter,
    PersonaLibraryEngine,
    PersonaProfileBuilder,
    PersonaSelector,
)
from backend.models import (
    PersonaLibraryEntry,
    PersonaSource,
    PersonaVersion,
)


def make_source() -> PersonaSource:
    return PersonaSource(
        id="source-architect",
        name="Architect Persona Notes",
        source_type="notes",
        content=(
            "traits: structured, careful\n"
            "values: clarity, modularity\n"
            "thinking_patterns: boundary-first reasoning\n"
            "communication_style: precise, calm"
        ),
        metadata={
            "persona_name": "Architect",
            "confidence": 0.92,
        },
    )


def make_version(
    profile_name: str,
    profile_snapshot: dict,
) -> PersonaVersion:
    return PersonaVersion(
        id="architect-version-1",
        persona_name=profile_name,
        version="1.0",
        created_at="2026-07-15",
        profile_snapshot=profile_snapshot,
        source_ids=["source-architect"],
        change_note="Initial imported profile snapshot.",
    )


def test_persona_library_lifecycle_from_import_to_selection() -> None:
    source = make_source()
    importer = PersonaImporter()
    builder = PersonaProfileBuilder()
    library = PersonaLibraryEngine()
    selector = PersonaSelector(library)
    activation_manager = PersonaActivationManager()

    import_result = importer.import_persona(source)
    profile = builder.build(import_result)
    profile_snapshot = {
        "name": profile.name,
        "traits": dict(profile.traits),
        "values": list(profile.values),
        "style": profile.style,
        "thinking_patterns": list(profile.thinking_patterns),
        "communication_style": list(profile.communication_style),
    }
    version = make_version(profile.name, profile_snapshot)
    original_version_snapshot = dict(version.profile_snapshot)

    entry = PersonaLibraryEntry(
        id="architect",
        name=profile.name,
        description="Imported architect persona.",
        profile=profile,
        versions=[version],
        current_version_id=version.id,
        source_ids=[source.id],
    )
    library.add_persona(entry)

    assert source.metadata["persona_name"] == "Architect"
    assert import_result.persona_name == "Architect"
    assert profile.name == "Architect"
    assert version.persona_name == "Architect"
    assert entry.name == "Architect"

    assert selector.select("architect") is None
    assert activation_manager.activate(entry) is None

    review = entry.submit_for_review(
        reviewer="Morgan",
        notes="Ready for lifecycle review.",
    )
    assert review.persona_entry_id == "architect"
    assert selector.select("architect") is None
    assert activation_manager.activate(entry) is None

    approval = entry.approve(
        reviewer="Morgan",
        notes="Approved for activation.",
    )
    assert approval.persona_entry_id == "architect"
    assert selector.select("architect") is None

    activation = activation_manager.activate(
        entry,
        activated_by="Morgan",
        activated_at="2026-07-15",
    )
    selected = selector.select("architect")

    assert activation is not None
    assert activation.persona_entry_id == "architect"
    assert activation.persona_version_id == version.id
    assert selected is entry
    assert selected.name == "Architect"
    assert selected.profile is profile
    assert selected.current_version_id == "architect-version-1"
    assert selected.versions[0].profile_snapshot == original_version_snapshot
    assert version.profile_snapshot == original_version_snapshot


def test_draft_persona_cannot_be_selected_in_lifecycle_pipeline() -> None:
    library = PersonaLibraryEngine()
    selector = PersonaSelector(library)
    version = make_version("Draft Architect", {"name": "Draft Architect"})
    draft_entry = PersonaLibraryEntry(
        id="draft-architect",
        name="Draft Architect",
        versions=[version],
        current_version_id=version.id,
    )

    library.add_persona(draft_entry)

    assert selector.select("draft-architect") is None


def test_rejected_persona_cannot_be_selected_in_lifecycle_pipeline() -> None:
    library = PersonaLibraryEngine()
    selector = PersonaSelector(library)
    activation_manager = PersonaActivationManager()
    version = make_version(
        "Rejected Architect",
        {"name": "Rejected Architect"},
    )
    rejected_entry = PersonaLibraryEntry(
        id="rejected-architect",
        name="Rejected Architect",
        versions=[version],
        current_version_id=version.id,
    )
    rejected_entry.submit_for_review(reviewer="Morgan")
    rejected_entry.reject(reviewer="Morgan", notes="Not ready.")

    library.add_persona(rejected_entry)

    assert activation_manager.activate(rejected_entry) is None
    assert selector.select("rejected-architect") is None
