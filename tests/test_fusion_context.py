"""Tests for persona-memory fusion context models."""

from backend.models import FusionContext


def test_fusion_context_initializes_with_values() -> None:
    context = FusionContext(
        memory_id="memory-1",
        memory_content="User prefers careful architecture changes.",
        persona_name="Architect",
        interpretation="This memory is relevant to modular design decisions.",
        relevance_score=0.85,
        confidence=0.9,
    )

    assert context.memory_id == "memory-1"
    assert context.memory_content == "User prefers careful architecture changes."
    assert context.persona_name == "Architect"
    assert context.interpretation == (
        "This memory is relevant to modular design decisions."
    )
    assert context.relevance_score == 0.85
    assert context.confidence == 0.9


def test_fusion_context_default_values_work() -> None:
    context = FusionContext()

    assert context.memory_id == ""
    assert context.memory_content == ""
    assert context.persona_name == ""
    assert context.interpretation == ""
    assert context.relevance_score == 0.0
    assert context.confidence == 0.0
