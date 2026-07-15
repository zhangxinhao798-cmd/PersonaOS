"""Tests for persona version boundary models."""

from backend.models import PersonaVersion


def test_persona_version_initializes_correctly() -> None:
    version = PersonaVersion(
        id="version-1",
        persona_name="Reflective Analyst",
        version="1.0.0",
        created_at="2026-07-15T00:00:00Z",
        profile_snapshot={"name": "Reflective Analyst"},
        source_ids=["source-1"],
        change_note="Initial imported persona profile.",
    )

    assert version.id == "version-1"
    assert version.persona_name == "Reflective Analyst"
    assert version.version == "1.0.0"
    assert version.created_at == "2026-07-15T00:00:00Z"
    assert version.profile_snapshot == {"name": "Reflective Analyst"}
    assert version.source_ids == ["source-1"]
    assert version.change_note == "Initial imported persona profile."


def test_persona_version_stores_profile_snapshot() -> None:
    snapshot = {
        "name": "Reflective Analyst",
        "traits": {"trait_1": "careful"},
        "values": ["clarity"],
    }

    version = PersonaVersion(profile_snapshot=snapshot)

    assert version.profile_snapshot == snapshot


def test_persona_version_stores_source_ids() -> None:
    version = PersonaVersion(source_ids=["source-1", "source-2"])

    assert version.source_ids == ["source-1", "source-2"]


def test_persona_version_empty_values_do_not_crash() -> None:
    version = PersonaVersion()

    assert version.id == ""
    assert version.persona_name == ""
    assert version.version == ""
    assert version.created_at == ""
    assert version.profile_snapshot == {}
    assert version.source_ids == []
    assert version.change_note == ""
