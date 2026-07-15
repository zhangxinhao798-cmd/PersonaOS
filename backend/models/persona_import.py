"""Persona import result boundary models for PersonaOS."""

from dataclasses import dataclass, field


@dataclass
class PersonaImportResult:
    """Result data boundary for future persona source analysis."""

    source_id: str = ""
    persona_name: str = ""
    traits: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    thinking_patterns: list[str] = field(default_factory=list)
    communication_style: list[str] = field(default_factory=list)
    speech_patterns: list[str] = field(default_factory=list)
    examples: list[dict] = field(default_factory=list)
    confidence: float = 0.0
