"""Memory record model for PersonaOS."""


class MemoryRecord:
    """Represents a single persistent memory."""

    def __init__(
        self,
        content: str,
        category: str,
        confidence: float,
        importance: float,
        source: str,
        timestamp: str,
    ) -> None:
        self.content = content
        self.category = category
        self.confidence = confidence
        self.importance = importance
        self.source = source
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return (
            "MemoryRecord("
            f"content={self.content!r}, "
            f"category={self.category!r}, "
            f"confidence={self.confidence!r}, "
            f"importance={self.importance!r}, "
            f"source={self.source!r}, "
            f"timestamp={self.timestamp!r}"
            ")"
        )
