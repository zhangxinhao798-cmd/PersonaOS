"""Tests for runtime context boundary models."""

from backend.models import RuntimeContext


def test_runtime_context_initializes_with_values() -> None:
    context = RuntimeContext(
        active_persona={"name": "Architect"},
        persona_version="v1",
        memories=["memory"],
        knowledge={"records": ["knowledge"], "sources": ["source"]},
        skills=["skill"],
        confidence={"score": 0.8},
        fusion_context=["fusion"],
        metadata={"query": "test"},
    )

    assert context.active_persona == {"name": "Architect"}
    assert context.persona_version == "v1"
    assert context.memories == ["memory"]
    assert context.knowledge == {
        "records": ["knowledge"],
        "sources": ["source"],
    }
    assert context.skills == ["skill"]
    assert context.confidence == {"score": 0.8}
    assert context.fusion_context == ["fusion"]
    assert context.metadata == {"query": "test"}


def test_runtime_context_defaults_preserve_empty_boundaries() -> None:
    context = RuntimeContext()

    assert context.active_persona is None
    assert context.persona_version == ""
    assert context.memories == []
    assert context.knowledge == {}
    assert context.skills == []
    assert context.confidence is None
    assert context.fusion_context == []
    assert context.metadata == {}
