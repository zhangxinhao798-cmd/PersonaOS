"""Tests for persona import result boundary models."""

from backend.models import PersonaImportResult


def test_persona_import_result_initializes_correctly() -> None:
    result = PersonaImportResult(
        source_id="source-1",
        persona_name="Reflective Analyst",
        traits=["reflective", "analytical"],
        values=["clarity", "care"],
        thinking_patterns=["compare evidence before deciding"],
        communication_style=["calm", "structured"],
        confidence=0.82,
    )

    assert result.source_id == "source-1"
    assert result.persona_name == "Reflective Analyst"
    assert result.traits == ["reflective", "analytical"]
    assert result.values == ["clarity", "care"]
    assert result.thinking_patterns == [
        "compare evidence before deciding"
    ]
    assert result.communication_style == ["calm", "structured"]
    assert result.confidence == 0.82


def test_persona_import_result_list_defaults_are_independent() -> None:
    first = PersonaImportResult()
    second = PersonaImportResult()

    first.traits.append("careful")
    first.values.append("truthfulness")
    first.thinking_patterns.append("step-by-step reasoning")
    first.communication_style.append("concise")

    assert first.traits == ["careful"]
    assert first.values == ["truthfulness"]
    assert first.thinking_patterns == ["step-by-step reasoning"]
    assert first.communication_style == ["concise"]
    assert second.traits == []
    assert second.values == []
    assert second.thinking_patterns == []
    assert second.communication_style == []


def test_persona_import_result_confidence_value_can_be_stored() -> None:
    result = PersonaImportResult(confidence=0.65)

    assert result.confidence == 0.65
