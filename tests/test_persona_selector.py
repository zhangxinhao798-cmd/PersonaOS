"""Tests for persona selection layer."""

from backend.core import PersonaLibraryEngine, PersonaSelector
from backend.models import (
    PersonaKnowledge,
    PersonaLibraryEntry,
)
from backend.models.persona_library import PersonaSource


def make_entry(persona_id: str, name: str) -> PersonaLibraryEntry:
    entry = PersonaLibraryEntry(
        id=persona_id,
        name=name,
        description=f"{name} selector test entry.",
        source=PersonaSource(
            source_type="test",
            title=f"{name} source",
            description="Selector test source.",
        ),
        traits=["focused"],
        knowledge=PersonaKnowledge(
            beliefs=["Persona selection should be explicit."],
            principles=["Selection does not mutate persona identity."],
            examples=["Select a library entry before activation."],
        ),
    )
    entry.approve(reviewer="test-reviewer", notes="Approved for selection.")
    return entry


def test_select_existing_persona() -> None:
    library = PersonaLibraryEngine()
    entry = library.add_persona(make_entry("architect", "Architect"))
    selector = PersonaSelector(library)

    selected = selector.select("architect")

    assert selected is entry


def test_get_current_persona() -> None:
    library = PersonaLibraryEngine()
    entry = library.add_persona(make_entry("architect", "Architect"))
    selector = PersonaSelector(library)

    selector.select("architect")

    assert selector.get_current() is entry


def test_selecting_unknown_persona_returns_none() -> None:
    library = PersonaLibraryEngine()
    selector = PersonaSelector(library)

    selected = selector.select("missing")

    assert selected is None
    assert selector.get_current() is None


def test_rejected_persona_cannot_be_selected() -> None:
    library = PersonaLibraryEngine()
    entry = PersonaLibraryEntry(id="architect", name="Architect")
    entry.submit_for_review(reviewer="test-reviewer")
    entry.reject(reviewer="test-reviewer", notes="Blocked from selection.")
    library.add_persona(entry)
    selector = PersonaSelector(library)

    selected = selector.select("architect")

    assert selected is None
    assert selector.get_current() is None


def test_clear_current_persona() -> None:
    library = PersonaLibraryEngine()
    library.add_persona(make_entry("architect", "Architect"))
    selector = PersonaSelector(library)
    selector.select("architect")

    selector.clear()

    assert selector.get_current() is None
