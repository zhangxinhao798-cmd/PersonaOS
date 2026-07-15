"""Persona library boundary models for PersonaOS."""

from dataclasses import dataclass, field

from backend.models.persona_profile import PersonaProfile
from backend.models.persona_version import PersonaVersion


@dataclass
class PersonaSource:
    """Source metadata for a persona library entry."""

    source_type: str = field(default_factory=str)
    title: str = field(default_factory=str)
    description: str = field(default_factory=str)


@dataclass
class PersonaKnowledge:
    """Structured knowledge attached to a persona library entry."""

    beliefs: list[str] = field(default_factory=list)
    principles: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


@dataclass
class PersonaLibraryEntry:
    """Stored persona library entry data boundary."""

    id: str = field(default_factory=str)
    name: str = field(default_factory=str)
    description: str = field(default_factory=str)
    lifecycle_state: str = "draft"
    current_version_id: str = field(default_factory=str)
    profile: PersonaProfile | None = None
    versions: list[PersonaVersion] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    source: PersonaSource = field(default_factory=PersonaSource)
    traits: list[str] = field(default_factory=list)
    knowledge: PersonaKnowledge = field(default_factory=PersonaKnowledge)
