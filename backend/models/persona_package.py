"""Persona package boundary models for PersonaOS."""

from dataclasses import dataclass, field

from backend.models.persona_profile import PersonaProfile
from backend.models.persona_source import PersonaSource


@dataclass
class PersonaPackageManifest:
    """Manifest metadata for a file-backed persona package."""

    package_id: str = ""
    name: str = ""
    version: str = ""
    description: str = ""
    profile_path: str = "profile.json"
    examples_path: str = "examples.json"
    sources_path: str = "sources.json"
    knowledge_path: str = "knowledge.json"
    metadata: dict = field(default_factory=dict)


@dataclass
class PersonaPackage:
    """Loaded persona package data before review or activation."""

    manifest: PersonaPackageManifest = field(
        default_factory=PersonaPackageManifest
    )
    profile: PersonaProfile | None = None
    examples: list[dict] = field(default_factory=list)
    sources: list[PersonaSource] = field(default_factory=list)
    knowledge: dict = field(default_factory=dict)
    package_path: str = ""


@dataclass
class PersonaPackageValidationResult:
    """Validation result for a persona package directory."""

    is_valid: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

