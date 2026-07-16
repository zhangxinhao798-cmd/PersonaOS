"""Persona repository boundary for PersonaOS."""

from typing import Protocol

from backend.models.persona_library import PersonaLibraryEntry


class PersonaRepository(Protocol):
    """Storage boundary for persona library entries."""

    def save(self, entry: PersonaLibraryEntry) -> None:
        """Save or replace a persona library entry."""

    def get(self, persona_id: str) -> PersonaLibraryEntry | None:
        """Return a persona library entry by id."""

    def list(self) -> list[PersonaLibraryEntry]:
        """Return all persona library entries."""

    def delete(self, persona_id: str) -> bool:
        """Delete a persona library entry and return whether one was removed."""


class InMemoryPersonaRepository:
    """In-memory PersonaRepository implementation.

    This repository does not create personas or modify profile/version data. It
    only stores entries explicitly handed to it.
    """

    def __init__(self) -> None:
        self._entries: dict[str, PersonaLibraryEntry] = {}

    def save(self, entry: PersonaLibraryEntry) -> None:
        self._entries[entry.id] = entry

    def get(self, persona_id: str) -> PersonaLibraryEntry | None:
        return self._entries.get(persona_id)

    def list(self) -> list[PersonaLibraryEntry]:
        return list(self._entries.values())

    def delete(self, persona_id: str) -> bool:
        if persona_id not in self._entries:
            return False

        del self._entries[persona_id]
        return True

