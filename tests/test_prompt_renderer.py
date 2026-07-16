"""Tests for PromptRenderer and FinalPrompt runtime boundaries."""

from backend.engine.prompt_renderer import PromptRenderer
from backend.models import FinalPrompt, PromptPackage


def test_final_prompt_initializes_with_values() -> None:
    prompt = FinalPrompt(
        text="rendered prompt",
        metadata={"trace_id": "final-1"},
    )

    assert prompt.text == "rendered prompt"
    assert prompt.metadata == {"trace_id": "final-1"}


def test_final_prompt_defaults_are_independent() -> None:
    first = FinalPrompt()
    second = FinalPrompt()

    first.metadata["trace_id"] = "first"

    assert first.text == ""
    assert first.metadata == {"trace_id": "first"}
    assert second.metadata == {}


def test_renders_empty_prompt_package() -> None:
    rendered = PromptRenderer().render(PromptPackage())

    assert isinstance(rendered, FinalPrompt)
    assert rendered.text == (
        "## System\n{}"
        "\n\n## Persona\n{}"
        "\n\n## Memory\n[]"
        "\n\n## Knowledge\n{}"
        "\n\n## Skills\n[]"
        "\n\n## Expression\n{}"
        "\n\n## Conversation\n[]"
        "\n\n## User Input\n"
        "\n\n## Metadata\n{}"
    )
    assert rendered.metadata == {}


def test_renders_full_prompt_package() -> None:
    metadata = {"trace_id": "render-1"}
    package = PromptPackage(
        system={"boundary": "PromptBuilder"},
        persona={"active_persona": {"name": "Architect"}},
        memory=["memory"],
        knowledge={"records": ["knowledge"], "sources": ["source"]},
        skills=["skill"],
        expression={"catchphrases": ["Keep the boundary."]},
        conversation=["previous turn"],
        user_input="current request",
        metadata=metadata,
    )

    rendered = PromptRenderer().render(package)

    assert "## System\n" in rendered.text
    assert '"boundary": "PromptBuilder"' in rendered.text
    assert "## Persona\n" in rendered.text
    assert '"name": "Architect"' in rendered.text
    assert "## Memory\n" in rendered.text
    assert '"memory"' in rendered.text
    assert "## Knowledge\n" in rendered.text
    assert '"knowledge"' in rendered.text
    assert "## Skills\n" in rendered.text
    assert '"skill"' in rendered.text
    assert "## Expression\n" in rendered.text
    assert '"Keep the boundary."' in rendered.text
    assert "## Conversation\n" in rendered.text
    assert '"previous turn"' in rendered.text
    assert "## User Input\ncurrent request" in rendered.text
    assert "## Metadata\n" in rendered.text
    assert '"trace_id": "render-1"' in rendered.text
    assert rendered.metadata is metadata


def test_renderer_preserves_section_ordering() -> None:
    rendered = PromptRenderer().render(PromptPackage(user_input="ordered"))

    headers = [
        line
        for line in rendered.text.splitlines()
        if line.startswith("## ")
    ]

    assert headers == [
        "## System",
        "## Persona",
        "## Memory",
        "## Knowledge",
        "## Skills",
        "## Expression",
        "## Conversation",
        "## User Input",
        "## Metadata",
    ]


def test_renderer_preserves_metadata() -> None:
    metadata = {"trace_id": "render-2", "source": "test"}
    package = PromptPackage(metadata=metadata)

    rendered = PromptRenderer().render(package)

    assert rendered.metadata is metadata


def test_renderer_output_is_deterministic() -> None:
    package = PromptPackage(
        system={"z": 1, "a": 2},
        knowledge={"sources": ["b", "a"], "records": ["knowledge"]},
        metadata={"trace_id": "stable"},
    )
    renderer = PromptRenderer()

    first = renderer.render(package)
    second = renderer.render(package)

    assert first.text == second.text
    assert first.metadata is second.metadata


def test_missing_optional_sections_render_as_empty_sections() -> None:
    package = PromptPackage(
        system=None,
        persona=None,
        memory=None,
        knowledge=None,
        skills=None,
        expression=None,
        conversation=None,
        metadata=None,
    )

    rendered = PromptRenderer().render(package)

    assert rendered.text == (
        "## System\n"
        "\n\n## Persona\n"
        "\n\n## Memory\n"
        "\n\n## Knowledge\n"
        "\n\n## Skills\n"
        "\n\n## Expression\n"
        "\n\n## Conversation\n"
        "\n\n## User Input\n"
        "\n\n## Metadata\n"
    )
    assert rendered.metadata == {}
