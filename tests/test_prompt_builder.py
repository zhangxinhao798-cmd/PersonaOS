"""Tests for PromptBuilder and PromptPackage runtime boundaries."""

from backend.engine.prompt_builder import PromptBuilder
from backend.models import PromptPackage, RuntimeContext


def test_prompt_package_initializes_with_values() -> None:
    package = PromptPackage(
        system={"boundary": "test"},
        persona={"active_persona": {"name": "Architect"}},
        relationship={"relationship_type": "companion"},
        memory=["memory"],
        knowledge={"records": ["knowledge"]},
        skills=["skill"],
        expression={"tone": "calm"},
        conversation=["previous turn"],
        user_input="current request",
        metadata={"trace_id": "prompt-1"},
    )

    assert package.system == {"boundary": "test"}
    assert package.persona == {"active_persona": {"name": "Architect"}}
    assert package.relationship == {"relationship_type": "companion"}
    assert package.memory == ["memory"]
    assert package.knowledge == {"records": ["knowledge"]}
    assert package.skills == ["skill"]
    assert package.expression == {"tone": "calm"}
    assert package.conversation == ["previous turn"]
    assert package.user_input == "current request"
    assert package.metadata == {"trace_id": "prompt-1"}


def test_prompt_package_defaults_are_independent() -> None:
    first = PromptPackage()
    second = PromptPackage()

    first.system["boundary"] = "first"
    first.relationship["relationship_type"] = "companion"
    first.memory.append("memory")
    first.knowledge["records"] = ["knowledge"]
    first.skills.append("skill")
    first.expression["tone"] = "first"
    first.conversation.append("turn")
    first.metadata["trace_id"] = "first"

    assert second.system == {}
    assert second.relationship == {}
    assert second.memory == []
    assert second.knowledge == {}
    assert second.skills == []
    assert second.expression == {}
    assert second.conversation == []
    assert second.metadata == {}


def test_builds_prompt_package_from_empty_runtime_context() -> None:
    package = PromptBuilder().build(RuntimeContext(), "hello")

    assert package.system["boundary"] == "PromptBuilder"
    assert package.system["provider_request"] is False
    assert package.persona == {
        "active_persona": None,
        "persona_version": "",
    }
    assert package.relationship == {}
    assert package.memory == []
    assert package.knowledge == {}
    assert package.skills == []
    assert package.expression == {}
    assert package.conversation == []
    assert package.user_input == "hello"
    assert package.metadata == {}


def test_builds_prompt_package_from_full_runtime_context() -> None:
    runtime_context = RuntimeContext(
        active_persona={"name": "Architect"},
        persona_version="v2",
        relationship={
            "relationship_type": "mentor",
            "interaction_style": "direct",
            "tone": "focused",
        },
        memories=["memory"],
        knowledge={"records": ["knowledge"], "sources": ["source"]},
        skills=["skill"],
        expression={
            "tone": "calm",
            "catchphrases": ["Let's preserve the boundary first."],
        },
        confidence={"score": 0.8},
        fusion_context=["fusion"],
        metadata={
            "query": "runtime prompt",
            "conversation": ["previous turn"],
            "source_boundaries": {"memories": "RuntimeContext.memories"},
        },
    )

    package = PromptBuilder().build(runtime_context, "current turn")

    assert package.persona["active_persona"] is runtime_context.active_persona
    assert package.persona["persona_version"] == "v2"
    assert package.relationship is runtime_context.relationship
    assert package.relationship["relationship_type"] == "mentor"
    assert package.memory is runtime_context.memories
    assert package.knowledge is runtime_context.knowledge
    assert package.skills is runtime_context.skills
    assert package.expression is runtime_context.expression
    assert package.expression["catchphrases"] == [
        "Let's preserve the boundary first."
    ]
    assert package.conversation is runtime_context.metadata["conversation"]
    assert package.user_input == "current turn"
    assert package.metadata is runtime_context.metadata
    assert package.metadata["source_boundaries"] == {
        "memories": "RuntimeContext.memories"
    }


def test_missing_optional_sections_default_to_empty_boundaries() -> None:
    runtime_context = RuntimeContext(
        memories=None,
        knowledge=None,
        skills=None,
        relationship=None,
        expression=None,
        metadata=None,
    )

    package = PromptBuilder().build(runtime_context)

    assert package.memory == []
    assert package.relationship == {}
    assert package.knowledge == {}
    assert package.skills == []
    assert package.expression == {}
    assert package.conversation == []
    assert package.metadata == {}


def test_prompt_package_section_order_is_deterministic() -> None:
    package = PromptBuilder().build(RuntimeContext(), "ordered")

    assert [name for name, _value in package.ordered_sections()] == [
        "system",
        "persona",
        "relationship",
        "memory",
        "knowledge",
        "skills",
        "expression",
        "conversation",
        "user_input",
        "metadata",
    ]


def test_builder_preserves_explicit_conversation_input() -> None:
    runtime_context = RuntimeContext(
        metadata={"conversation": ["metadata conversation"]},
    )
    conversation = ["explicit conversation"]

    package = PromptBuilder().build(
        runtime_context,
        "current",
        conversation=conversation,
    )

    assert package.conversation is conversation
    assert package.metadata is runtime_context.metadata
