"""Tests for persona library boundary models."""

from backend.models import (
    PersonaKnowledge,
    PersonaLibraryEntry,
)
from backend.models.persona_library import PersonaSource


def test_persona_source_creation() -> None:
    source = PersonaSource(
        source_type="manual",
        title="Investor Persona Notes",
        description="Source notes for a value-oriented persona.",
    )

    assert source.source_type == "manual"
    assert source.title == "Investor Persona Notes"
    assert source.description == "Source notes for a value-oriented persona."


def test_persona_knowledge_default_values() -> None:
    knowledge = PersonaKnowledge()

    assert knowledge.beliefs == []
    assert knowledge.principles == []
    assert knowledge.examples == []


def test_persona_library_entry_creation() -> None:
    source = PersonaSource(
        source_type="document",
        title="Reflective Coach",
        description="Imported persona design notes.",
    )
    knowledge = PersonaKnowledge(
        beliefs=["Experience can be interpreted from multiple perspectives."],
        principles=["Preserve identity boundaries."],
        examples=["Ask what the memory means before acting on it."],
    )

    entry = PersonaLibraryEntry(
        id="reflective-coach",
        name="Reflective Coach",
        description="A persona focused on self-reflection.",
        source=source,
        traits=["reflective", "careful"],
        knowledge=knowledge,
    )

    assert entry.id == "reflective-coach"
    assert entry.name == "Reflective Coach"
    assert entry.description == "A persona focused on self-reflection."
    assert entry.traits == ["reflective", "careful"]


def test_persona_library_entry_nested_data_works() -> None:
    entry = PersonaLibraryEntry(
        source=PersonaSource(
            source_type="seed",
            title="Value Investor",
            description="Seed profile for investment reasoning.",
        ),
        knowledge=PersonaKnowledge(
            beliefs=["Losses should be reviewed with context."],
            principles=["Separate evidence from reaction."],
            examples=["Compare price, value, and risk before deciding."],
        ),
    )

    assert entry.source.title == "Value Investor"
    assert entry.knowledge.beliefs == [
        "Losses should be reviewed with context."
    ]
    assert entry.knowledge.principles == [
        "Separate evidence from reaction."
    ]
    assert entry.knowledge.examples == [
        "Compare price, value, and risk before deciding."
    ]
