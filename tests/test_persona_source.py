"""Tests for external persona source boundary models."""

from backend.models import PersonaSource


def test_persona_source_initializes_correctly() -> None:
    source = PersonaSource(
        id="source-1",
        name="Interview Notes",
        source_type="user notes",
        content="Persona notes from a long-form interview.",
        metadata={"author": "tester"},
    )

    assert source.id == "source-1"
    assert source.name == "Interview Notes"
    assert source.source_type == "user notes"
    assert source.content == "Persona notes from a long-form interview."
    assert source.metadata == {"author": "tester"}


def test_persona_source_default_metadata_is_independent() -> None:
    first = PersonaSource()
    second = PersonaSource()

    first.metadata["format"] = "transcript"

    assert first.metadata == {"format": "transcript"}
    assert second.metadata == {}


def test_persona_source_fields_can_be_accessed_and_modified() -> None:
    source = PersonaSource()

    source.id = "source-2"
    source.name = "Conversation Export"
    source.source_type = "conversation export"
    source.content = "Exported conversation text."
    source.metadata["turns"] = 12

    assert source.id == "source-2"
    assert source.name == "Conversation Export"
    assert source.source_type == "conversation export"
    assert source.content == "Exported conversation text."
    assert source.metadata == {"turns": 12}
