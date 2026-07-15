"""Persona Library Engine v1."""

from backend.models.persona_library import PersonaLibraryEntry


class PersonaLibraryEngine:
    """Manages in-memory persona library entries.

    The Persona Library owns available persona records only. It does not
    activate personas, mutate PersonaEngine state, persist files, or call
    external model providers.
    """

    def __init__(self) -> None:
        self._personas: dict[str, PersonaLibraryEntry] = {}

    def add_persona(
        self,
        persona: PersonaLibraryEntry,
    ) -> PersonaLibraryEntry:
        """Store a persona library entry and return it."""

        self._personas[persona.id] = persona
        return persona

    def get_persona(
        self,
        persona_id: str,
    ) -> PersonaLibraryEntry | None:
        """Return a stored persona by id, or None if it is absent."""

        return self._personas.get(persona_id)

    def list_personas(self) -> list[PersonaLibraryEntry]:
        """Return all stored persona library entries."""

        return list(self._personas.values())

    def remove_persona(
        self,
        persona_id: str,
    ) -> PersonaLibraryEntry | None:
        """Remove a persona library entry and return it if present."""

        return self._personas.pop(persona_id, None)
