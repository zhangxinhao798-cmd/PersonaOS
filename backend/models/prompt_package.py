"""Structured prompt package model for PersonaOS runtime boundaries."""

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class PromptPackage:
    """Structured runtime artifact prepared for prompt construction.

    This package keeps prompt sections separated. It is not a provider request
    and does not represent a final flattened prompt string.
    """

    SECTION_ORDER: ClassVar[tuple[str, ...]] = (
        "system",
        "persona",
        "memory",
        "knowledge",
        "skills",
        "conversation",
        "user_input",
        "metadata",
    )

    system: dict = field(default_factory=dict)
    persona: dict = field(default_factory=dict)
    memory: list = field(default_factory=list)
    knowledge: dict = field(default_factory=dict)
    skills: list = field(default_factory=list)
    conversation: list = field(default_factory=list)
    user_input: str = ""
    metadata: dict = field(default_factory=dict)

    def ordered_sections(self) -> list[tuple[str, Any]]:
        """Return prompt sections in deterministic runtime order."""

        return [
            (section_name, getattr(self, section_name))
            for section_name in self.SECTION_ORDER
        ]

