"""ConfidenceEngine tests."""

from backend.core.confidence import ConfidenceEngine
from backend.models.memory_record import MemoryRecord


def make_memory(confidence: float = 0.5, source: str = "test") -> MemoryRecord:
    """Create a simple memory record for confidence tests."""

    return MemoryRecord(
        content="Confidence test memory.",
        category="semantic",
        confidence=confidence,
        importance=0.5,
        source=source,
        timestamp="2026-07-15T00:00:00Z",
    )


def test_calculate_confidence_returns_initial_memory_confidence() -> None:
    """Neutral source reliability should preserve initial confidence."""

    engine = ConfidenceEngine()
    memory = make_memory(confidence=0.6)

    assert engine.calculate_confidence(memory) == 0.6


def test_update_confidence_increases_with_positive_evidence() -> None:
    """Positive evidence should increase memory confidence."""

    engine = ConfidenceEngine()
    memory = make_memory(confidence=0.5)
    initial_confidence = engine.calculate_confidence(memory)

    updated_confidence = engine.update_confidence(
        memory,
        evidence_strength=0.5,
    )

    assert updated_confidence > initial_confidence


def test_update_confidence_decreases_with_negative_evidence() -> None:
    """Negative evidence should decrease memory confidence."""

    engine = ConfidenceEngine()
    memory = make_memory(confidence=0.7)
    initial_confidence = engine.calculate_confidence(memory)

    updated_confidence = engine.update_confidence(
        memory,
        evidence_strength=-0.5,
    )

    assert updated_confidence < initial_confidence


def test_confidence_stays_within_valid_range() -> None:
    """Confidence updates should stay between 0.0 and 1.0."""

    engine = ConfidenceEngine()
    high_confidence_memory = make_memory(confidence=0.95)
    low_confidence_memory = make_memory(confidence=0.05)

    high_confidence = engine.update_confidence(
        high_confidence_memory,
        evidence_strength=10.0,
    )
    low_confidence = engine.update_confidence(
        low_confidence_memory,
        evidence_strength=-10.0,
    )

    assert 0.0 <= high_confidence <= 1.0
    assert 0.0 <= low_confidence <= 1.0
