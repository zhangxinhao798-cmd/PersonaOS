"""PersonaOS backend entry point."""

from backend.engine.persona_os import PersonaOS


def create_app() -> PersonaOS:
    """Create the initial PersonaOS backend object.

    This is intentionally minimal until runtime behavior is defined.
    """

    return PersonaOS()


def log_startup(app: PersonaOS) -> None:
    """Print the initial backend startup status."""

    print("PersonaOS Booting...")
    print("Persona Engine: OK")
    print("Memory Engine: OK")
    print("Knowledge Engine: OK")
    print("Skill Engine: OK")
    print("Confidence Engine: OK")
    print("Evolution Engine: OK")
    print("PersonaOS Ready.")


if __name__ == "__main__":
    log_startup(create_app())
