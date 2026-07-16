"""Tests for Relationship Boundary v1."""

from backend.models import RelationshipContext
from backend.models.context import PersonaContext, PersonaOSContext


def test_relationship_context_initializes_with_values() -> None:
    relationship = RelationshipContext(
        relationship_type="companion",
        interaction_style="warm",
        tone="supportive",
        permissions=["chat"],
        lifecycle="active",
        metadata={"user_id": "local-user"},
    )

    assert relationship.relationship_type == "companion"
    assert relationship.interaction_style == "warm"
    assert relationship.tone == "supportive"
    assert relationship.permissions == ["chat"]
    assert relationship.lifecycle == "active"
    assert relationship.metadata == {"user_id": "local-user"}


def test_relationship_context_defaults_are_independent() -> None:
    first = RelationshipContext()
    second = RelationshipContext()

    first.permissions.append("chat")
    first.metadata["scope"] = "session"

    assert second.permissions == []
    assert second.metadata == {}


def test_relationship_context_is_detached_when_serialized() -> None:
    relationship = RelationshipContext(
        relationship_type="mentor",
        interaction_style="direct",
        tone="focused",
        permissions=["guidance"],
        metadata={"origin": "test"},
    )

    serialized = relationship.to_dict()
    serialized["permissions"].append("mutated")
    serialized["metadata"]["origin"] = "changed"

    assert relationship.permissions == ["guidance"]
    assert relationship.metadata == {"origin": "test"}


def test_persona_os_context_carries_relationship_without_mutating_persona() -> None:
    persona = PersonaContext(name="Architect", style="precise")
    relationship = RelationshipContext(
        relationship_type="companion",
        interaction_style="warm",
        tone="supportive",
    )

    context = PersonaOSContext(
        query="relationship boundary",
        persona=persona,
        relationship=relationship,
    )

    assert context.relationship is relationship
    assert context.persona is persona
    assert not hasattr(context.persona, "relationship_type")
