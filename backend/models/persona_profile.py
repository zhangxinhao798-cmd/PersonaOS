"""Persona profile model for PersonaOS."""

from dataclasses import dataclass, field


@dataclass
class PersonaProfile:
    """Represents a persistent persona identity."""

    name: str
    traits: dict[str, str]
    values: list[str]
    style: str
    boundaries: list[str]
    thinking_patterns: list[str] = field(default_factory=list)
    communication_style: list[str] = field(default_factory=list)
    speech_patterns: list[str] = field(default_factory=list)
    examples: list[dict] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            "PersonaProfile("
            f"name={self.name!r}, "
            f"traits={self.traits!r}, "
            f"values={self.values!r}, "
            f"style={self.style!r}, "
            f"boundaries={self.boundaries!r}, "
            f"thinking_patterns={self.thinking_patterns!r}, "
            f"communication_style={self.communication_style!r}, "
            f"speech_patterns={self.speech_patterns!r}, "
            f"examples={self.examples!r}"
            ")"
        )
