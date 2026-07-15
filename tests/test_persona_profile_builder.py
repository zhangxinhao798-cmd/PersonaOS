"""Tests for PersonaProfileBuilder transformation behavior."""

from backend.core import PersonaProfileBuilder
from backend.models import PersonaImportResult, PersonaProfile


def test_builder_converts_import_result_into_profile() -> None:
    result = PersonaImportResult(
        source_id="source-1",
        persona_name="Reflective Analyst",
        traits=["careful", "analytical"],
        values=["clarity"],
        thinking_patterns=["compare evidence before deciding"],
        communication_style=["calm", "structured"],
    )

    profile = PersonaProfileBuilder().build(result)

    assert isinstance(profile, PersonaProfile)
    assert profile.name == "Reflective Analyst"
    assert profile.traits == {
        "trait_1": "careful",
        "trait_2": "analytical",
    }
    assert profile.values == ["clarity"]
    assert profile.style == "calm, structured"
    assert profile.thinking_patterns == [
        "compare evidence before deciding"
    ]
    assert profile.communication_style == ["calm", "structured"]


def test_builder_preserves_speech_patterns() -> None:
    result = PersonaImportResult(
        speech_patterns=[
            "Let's slow down and inspect the evidence.",
            "A careful answer starts with context.",
        ]
    )

    profile = PersonaProfileBuilder().build(result)

    assert profile.speech_patterns == [
        "Let's slow down and inspect the evidence.",
        "A careful answer starts with context.",
    ]


def test_builder_preserves_examples() -> None:
    example = {
        "question": "How should uncertainty be handled?",
        "answer": "Name uncertainty before recommending action.",
    }
    result = PersonaImportResult(examples=[example])

    profile = PersonaProfileBuilder().build(result)

    assert profile.examples == [example]


def test_builder_empty_result_does_not_crash() -> None:
    profile = PersonaProfileBuilder().build(PersonaImportResult())

    assert isinstance(profile, PersonaProfile)
    assert profile.name == ""
    assert profile.traits == {}
    assert profile.values == []
    assert profile.style == ""
    assert profile.boundaries == []
    assert profile.thinking_patterns == []
    assert profile.communication_style == []
    assert profile.speech_patterns == []
    assert profile.examples == []
