"""Persona selection layer for PersonaOS."""

from backend.core.persona_library import PersonaLibraryEngine
from backend.models.persona_library import PersonaLibraryEntry


class PersonaSelector:
    """Selects an active persona entry from a Persona Library.

    Selection is in-memory only. This layer does not mutate PersonaEngine,
    call orchestration, persist files, or perform persona import logic.
    """

    def __init__(self, persona_library: PersonaLibraryEngine) -> None:
        self._persona_library = persona_library
        self._current: PersonaLibraryEntry | None = None

    def select(self, persona_id: str) -> PersonaLibraryEntry | None:
        """Select and return a persona library entry by id."""

        persona = self._persona_library.get_persona(persona_id)
        if persona is None:
            return None

        self._current = persona
        return persona

    def get_current(self) -> PersonaLibraryEntry | None:
        """Return the currently selected persona, if one exists."""

        return self._current

    def clear(self) -> None:
        """Clear the current persona selection."""

        self._current = None
