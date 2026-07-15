"""Skill Engine v1."""


class SkillRecord:
    """Represents a single governed PersonaOS capability.

    Skills are capabilities available to a digital mind. They are separate
    from personas and should remain explicit, inspectable records.
    """

    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        confidence: float,
        metadata: dict,
    ) -> None:
        self.name = name
        self.description = description
        self.category = category
        self.confidence = confidence
        self.metadata = metadata

    def __repr__(self) -> str:
        return (
            "SkillRecord("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"category={self.category!r}, "
            f"confidence={self.confidence!r}, "
            f"metadata={self.metadata!r}"
            ")"
        )


class SkillEngine:
    """Manages governed capabilities available to a digital mind.

    Skills are capabilities, not personalities. The Skill Engine should
    eventually discover, register, select, execute, evaluate, and evolve
    skills through explicit permission boundaries.
    """

    def __init__(self) -> None:
        self._skills: list[SkillRecord] = []

    def create_skill(self, skill: SkillRecord) -> SkillRecord:
        """Store a skill record and return it."""
        self._skills.append(skill)
        return skill

    def get_skills(self) -> list[SkillRecord]:
        """Return all stored skill records."""
        return self._skills

    def update_skill(
        self,
        skill: SkillRecord,
        name: str | None = None,
        description: str | None = None,
        category: str | None = None,
        confidence: float | None = None,
        metadata: dict | None = None,
    ) -> SkillRecord:
        """Update provided fields on a skill record and return it."""
        if name is not None:
            skill.name = name

        if description is not None:
            skill.description = description

        if category is not None:
            skill.category = category

        if confidence is not None:
            skill.confidence = confidence

        if metadata is not None:
            skill.metadata = metadata

        return skill

    def remove_skill(self, skill: SkillRecord) -> SkillRecord | None:
        """Remove a skill record from storage and return it if present."""
        if skill not in self._skills:
            return None

        self._skills.remove(skill)
        return skill
