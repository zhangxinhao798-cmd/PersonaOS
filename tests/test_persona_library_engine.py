"""Tests for Persona Library Engine management."""

from backend.core import PersonaLibraryEngine
from backend.models import (
    PersonaKnowledge,
    PersonaLibraryEntry,
    PersonaSource,
)


def make_entry(persona_id: str, name: str) -> PersonaLibraryEntry:
    return PersonaLibraryEntry(
        id=persona_id,
        name=name,
        description=f"{name} library entry.",
        source=PersonaSource(
            source_type="test",
            title=f"{name} source",
            description="Test persona source.",
        ),
        traits=["careful", "modular"],
        knowledge=PersonaKnowledge(
            beliefs=["Personas should remain explicit."],
            principles=["Keep identity separate from memory."],
            examples=["Load a persona before activating it."],
        ),
    )


def test_add_and_retrieve_persona() -> None:
    engine = PersonaLibraryEngine()
    entry = make_entry("architect", "Architect")

    result = engine.add_persona(entry)

    assert result is entry
    assert engine.get_persona("architect") is entry


def test_list_multiple_personas() -> None:
    engine = PersonaLibraryEngine()
    architect = engine.add_persona(make_entry("architect", "Architect"))
    coach = engine.add_persona(make_entry("coach", "Coach"))

    personas = engine.list_personas()

    assert personas == [architect, coach]


def test_remove_persona() -> None:
    engine = PersonaLibraryEngine()
    entry = engine.add_persona(make_entry("architect", "Architect"))

    removed = engine.remove_persona("architect")

    assert removed is entry
    assert engine.get_persona("architect") is None


def test_separate_instances_have_isolated_storage() -> None:
    first_engine = PersonaLibraryEngine()
    second_engine = PersonaLibraryEngine()
    entry = make_entry("architect", "Architect")

    first_engine.add_persona(entry)

    assert first_engine.get_persona("architect") is entry
    assert second_engine.get_persona("architect") is None
    assert second_engine.list_personas() == []
