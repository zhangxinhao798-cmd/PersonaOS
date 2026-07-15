"""Persona-memory fusion boundary models for PersonaOS."""

from dataclasses import dataclass, field


@dataclass
class FusionContext:
    """Structured persona-aware memory interpretation data."""

    memory_id: str = field(default_factory=str)
    memory_content: str = field(default_factory=str)
    persona_name: str = field(default_factory=str)
    interpretation: str = field(default_factory=str)
    relevance_score: float = field(default_factory=float)
    confidence: float = field(default_factory=float)
