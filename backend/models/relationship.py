"""Relationship boundary models for PersonaOS."""

from dataclasses import dataclass, field


@dataclass
class RelationshipContext:
    """User-persona relationship context for runtime use.

    Relationship is not persona identity. It describes how one user and one
    persona should interact in the current controlled runtime context.
    """

    relationship_type: str = ""
    interaction_style: str = ""
    tone: str = ""
    permissions: list[str] = field(default_factory=list)
    lifecycle: str = "active"
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.permissions = list(self.permissions or [])
        self.metadata = dict(self.metadata or {})

    def to_dict(self) -> dict:
        """Return a detached JSON-friendly relationship mapping."""

        return {
            "relationship_type": self.relationship_type,
            "interaction_style": self.interaction_style,
            "tone": self.tone,
            "permissions": list(self.permissions),
            "lifecycle": self.lifecycle,
            "metadata": dict(self.metadata),
        }
