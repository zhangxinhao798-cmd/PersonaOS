"""Tests for richer PersonaProfile identity fields."""

from backend.models import PersonaProfile


def make_profile() -> PersonaProfile:
    return PersonaProfile(
        name="Reflective Analyst",
        traits={"focus": "careful analysis"},
        values=["clarity"],
        style="calm",
        boundaries=["avoid unsupported claims"],
    )


def test_persona_profile_v2_fields_initialize_correctly() -> None:
    profile = PersonaProfile(
        name="Reflective Analyst",
        traits={"focus": "careful analysis"},
        values=["clarity"],
        style="calm",
        boundaries=["avoid unsupported claims"],
        thinking_patterns=["compare evidence before deciding"],
        communication_style=["structured"],
        speech_patterns=["Let's inspect the evidence first."],
        examples=[
            {
                "question": "What should we do?",
                "answer": "Start by separating evidence from assumptions.",
            }
        ],
    )

    assert profile.thinking_patterns == [
        "compare evidence before deciding"
    ]
    assert profile.communication_style == ["structured"]
    assert profile.speech_patterns == [
        "Let's inspect the evidence first."
    ]
    assert profile.examples == [
        {
            "question": "What should we do?",
            "answer": "Start by separating evidence from assumptions.",
        }
    ]


def test_persona_profile_v2_list_defaults_are_independent() -> None:
    first = make_profile()
    second = make_profile()

    first.thinking_patterns.append("reason step by step")
    first.communication_style.append("concise")
    first.speech_patterns.append("A careful answer starts with context.")
    first.examples.append(
        {
            "question": "Why pause?",
            "answer": "To avoid confusing memory with fact.",
        }
    )

    assert first.thinking_patterns == ["reason step by step"]
    assert first.communication_style == ["concise"]
    assert first.speech_patterns == [
        "A careful answer starts with context."
    ]
    assert first.examples == [
        {
            "question": "Why pause?",
            "answer": "To avoid confusing memory with fact.",
        }
    ]
    assert second.thinking_patterns == []
    assert second.communication_style == []
    assert second.speech_patterns == []
    assert second.examples == []


def test_persona_profile_v2_speech_patterns_store_phrases() -> None:
    profile = make_profile()

    profile.speech_patterns.append("Let's slow down and make it concrete.")

    assert profile.speech_patterns == [
        "Let's slow down and make it concrete."
    ]


def test_persona_profile_v2_examples_store_question_answer_examples() -> None:
    profile = make_profile()
    example = {
        "question": "How should uncertainty be handled?",
        "answer": "Name the uncertainty before making a recommendation.",
    }

    profile.examples.append(example)

    assert profile.examples == [example]
