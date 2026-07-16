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
