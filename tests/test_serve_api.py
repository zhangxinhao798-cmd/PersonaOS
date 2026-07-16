"""Tests for serve_api wiring helpers."""

from pathlib import Path

from backend.api import ApiTransport
from scripts.serve_api import LocalPersonaRuntimeProvider, build_api_transport


def test_build_api_transport_returns_transport_boundary() -> None:
    transport = build_api_transport(
        personas_dir=Path("personas"),
        default_persona_id="architect",
    )

    assert isinstance(transport, ApiTransport)


def test_local_runtime_provider_lists_personas_without_starting_server() -> None:
    provider = LocalPersonaRuntimeProvider(
        personas_dir=Path("personas"),
        default_persona_id="architect",
    )

    personas = provider.list_personas()

    assert any(persona["id"] == "architect" for persona in personas)
    architect = next(persona for persona in personas if persona["id"] == "architect")
    assert architect["style"] == "structured, concise, and careful"
    assert architect["traits"]["focus"] == "modular architecture"
    assert architect["suitable_scenarios"] == [
        "System architecture review",
        "Technical planning",
        "Boundary-focused implementation",
    ]
