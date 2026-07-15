"""Runtime context boundary models for PersonaOS."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeContext:
    """Runtime-ready context prepared for future model adapters.

    This model is a boundary object only. It preserves already-prepared
    PersonaOS context sections without retrieving, ranking, or interpreting
    engine-owned data.
    """

    active_persona: Any = None
    persona_version: str = ""
    memories: list = field(default_factory=list)
    knowledge: dict = field(default_factory=dict)
    skills: list = field(default_factory=list)
    confidence: Any = None
    fusion_context: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
