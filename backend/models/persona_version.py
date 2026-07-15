"""Persona version boundary models for PersonaOS."""

from dataclasses import dataclass, field


@dataclass
class PersonaVersion:
    """Version snapshot for a persona profile."""

    id: str = ""
    persona_name: str = ""
    version: str = ""
    created_at: str = ""
    profile_snapshot: dict = field(default_factory=dict)
    source_ids: list[str] = field(default_factory=list)
    change_note: str = ""
