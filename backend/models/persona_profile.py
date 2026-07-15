"""Persona profile model for PersonaOS."""


class PersonaProfile:
    """Represents a persistent persona identity."""

    def __init__(
        self,
        name: str,
        traits: dict[str, str],
        values: list[str],
        style: str,
        boundaries: list[str],
    ) -> None:
        self.name = name
        self.traits = traits
        self.values = values
        self.style = style
        self.boundaries = boundaries

    def __repr__(self) -> str:
        return (
            "PersonaProfile("
            f"name={self.name!r}, "
            f"traits={self.traits!r}, "
            f"values={self.values!r}, "
            f"style={self.style!r}, "
            f"boundaries={self.boundaries!r}"
            ")"
        )
