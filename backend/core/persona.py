"""Persona Engine skeleton."""

from backend.models.persona_profile import PersonaProfile


class PersonaEngine:
    """Coordinates identity, behavior, and the active operating frame.

    The Persona Engine should remain the central coordinator for a digital
    mind without owning memory, knowledge, skills, confidence, or evolution.
    """

    def __init__(self) -> None:
        self._profile = PersonaProfile(
            name="Default Persona",
            traits={},
            values=[],
            style="",
            boundaries=[],
        )

    def set_trait(self, name: str, value: str) -> str:
        """Store or update a persona trait and return its value."""

        self._profile.traits[name] = value
        return value

    def get_trait(self, name: str) -> str | None:
        """Return a persona trait value, or None if it does not exist."""

        return self._profile.traits.get(name)

    def get_profile(self) -> PersonaProfile:
        """Return the current persona profile."""

        return self._profile

    def describe_persona(self) -> str:
        """Return a readable description of the current persona profile.

        Future versions can replace this with structured persona profiles,
        versioned configuration, and controlled evolution proposals.
        """

        profile = self._profile
        parts = [f"Persona: {profile.name}"]

        if profile.traits:
            traits = [
                f"{name}: {value}"
                for name, value in sorted(profile.traits.items())
            ]
            parts.append("Traits: " + "; ".join(traits))
        else:
            parts.append("Traits: none")

        if profile.values:
            parts.append("Values: " + "; ".join(profile.values))

        if profile.style:
            parts.append(f"Style: {profile.style}")

        if profile.boundaries:
            parts.append("Boundaries: " + "; ".join(profile.boundaries))

        return " | ".join(parts)
