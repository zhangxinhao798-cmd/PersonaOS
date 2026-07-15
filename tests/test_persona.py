"""PersonaEngine tests."""

from backend.core.persona import PersonaEngine
from backend.models.persona_profile import PersonaProfile


def test_persona_engine_creates_default_persona_profile() -> None:
    """PersonaEngine should initialize with a default PersonaProfile."""

    engine = PersonaEngine()

    assert isinstance(engine.get_profile(), PersonaProfile)
    assert engine.get_profile().name == "Default Persona"


def test_set_trait_stores_persona_traits() -> None:
    """PersonaEngine should store traits on the active profile."""

    engine = PersonaEngine()

    engine.set_trait("role", "architect")

    assert engine.get_profile().traits["role"] == "architect"


def test_get_trait_returns_stored_traits() -> None:
    """PersonaEngine should return stored trait values."""

    engine = PersonaEngine()

    engine.set_trait("tone", "calm")

    assert engine.get_trait("tone") == "calm"


def test_get_profile_returns_persona_profile() -> None:
    """PersonaEngine should expose the current PersonaProfile."""

    engine = PersonaEngine()

    profile = engine.get_profile()

    assert isinstance(profile, PersonaProfile)


def test_describe_persona_returns_readable_persona_information() -> None:
    """PersonaEngine should describe the current profile in readable text."""

    engine = PersonaEngine()

    engine.set_trait("focus", "memory architecture")

    description = engine.describe_persona()

    assert "Default Persona" in description
    assert "focus: memory architecture" in description
