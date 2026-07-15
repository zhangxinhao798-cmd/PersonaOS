"""Evolution Engine v1."""


class EvolutionRecord:
    """Represents a proposed controlled change to PersonaOS state.

    Evolution records describe what could change and why. Applying an
    evolution is explicit and does not automatically modify other engines.
    """

    def __init__(
        self,
        target: str,
        change: str,
        reason: str,
        confidence: float,
        timestamp: str,
    ) -> None:
        self.target = target
        self.change = change
        self.reason = reason
        self.confidence = confidence
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return (
            "EvolutionRecord("
            f"target={self.target!r}, "
            f"change={self.change!r}, "
            f"reason={self.reason!r}, "
            f"confidence={self.confidence!r}, "
            f"timestamp={self.timestamp!r}"
            ")"
        )


class EvolutionEngine:
    """Governs controlled long-term change.

    The Evolution Engine should eventually detect, propose, evaluate,
    approve, apply, version, and roll back durable changes while preserving
    identity and preventing personality drift.
    """

    def __init__(self) -> None:
        self._evolutions: list[EvolutionRecord] = []
        self._applied_evolutions: list[EvolutionRecord] = []

    def propose_evolution(
        self,
        evolution: EvolutionRecord,
    ) -> EvolutionRecord:
        """Store an explicit evolution proposal and return it."""
        self._evolutions.append(evolution)
        return evolution

    def get_evolutions(self) -> list[EvolutionRecord]:
        """Return all proposed evolution records."""
        return self._evolutions

    def apply_evolution(
        self,
        evolution: EvolutionRecord,
    ) -> EvolutionRecord | None:
        """Mark a proposed evolution as applied without mutating targets."""
        if evolution not in self._evolutions:
            return None

        if evolution not in self._applied_evolutions:
            self._applied_evolutions.append(evolution)

        return evolution
