"""Persona activation boundary for PersonaOS."""

from backend.models.persona_library import (
    PersonaActivation,
    PersonaActivationStatus,
    PersonaLibraryEntry,
)


class PersonaActivationManager:
    """Controls activation of approved persona library entries.

    Activation is in-memory only. It records runtime availability without
    mutating PersonaEngine, PersonaVersion snapshots, or orchestration state.
    """

    def __init__(self) -> None:
        self._personas: dict[str, PersonaLibraryEntry] = {}

    def activate(
        self,
        persona_entry: PersonaLibraryEntry,
        activated_by: str = "",
        activated_at: str = "",
        activation_id: str = "",
    ) -> PersonaActivation | None:
        """Activate an approved entry with a valid current version."""

        if not persona_entry.is_approved_for_activation():
            return None
        if not persona_entry.has_valid_current_version():
            return None

        self.deactivate(persona_entry)
        activation = PersonaActivation(
            activation_id=activation_id
            or self._next_activation_id(persona_entry),
            persona_entry_id=persona_entry.id,
            persona_version_id=persona_entry.current_version_id,
            activated_at=activated_at,
            activated_by=activated_by,
            status=PersonaActivationStatus.ACTIVE,
        )
        persona_entry.activations.append(activation)
        self._personas[persona_entry.id] = persona_entry
        return activation

    def deactivate(
        self,
        persona_entry: PersonaLibraryEntry,
    ) -> PersonaActivation | None:
        """Deactivate the current activation without deleting history."""

        self._personas[persona_entry.id] = persona_entry
        for activation in reversed(persona_entry.activations):
            if activation.status == PersonaActivationStatus.ACTIVE:
                activation.status = PersonaActivationStatus.INACTIVE
                return activation
        return None

    def get_active_personas(self) -> list[PersonaLibraryEntry]:
        """Return approved entries that currently have valid activation."""

        return [
            persona
            for persona in self._personas.values()
            if persona.is_selectable()
        ]

    def _next_activation_id(
        self,
        persona_entry: PersonaLibraryEntry,
    ) -> str:
        entry_id = persona_entry.id or "persona-entry"
        return f"{entry_id}-activation-{len(persona_entry.activations) + 1}"
