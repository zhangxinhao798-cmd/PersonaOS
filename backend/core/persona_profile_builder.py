"""Persona profile builder boundary for PersonaOS."""

from backend.models.persona_import import PersonaImportResult
from backend.models.persona_profile import PersonaProfile


class PersonaProfileBuilder:
    """Builds PersonaProfile objects from persona import results.

    This builder is deterministic and data-only. It does not activate
    personas, persist data, or call model providers.
    """

    def build(self, result: PersonaImportResult) -> PersonaProfile:
        """Build a PersonaProfile from an import result."""

        return PersonaProfile(
            name=result.persona_name,
            traits=self._build_traits(result.traits),
            values=list(result.values),
            style=", ".join(result.communication_style),
            boundaries=[],
            thinking_patterns=list(result.thinking_patterns),
            communication_style=list(result.communication_style),
            speech_patterns=list(result.speech_patterns),
            examples=list(result.examples),
        )

    def _build_traits(self, traits: list[str]) -> dict[str, str]:
        return {
            f"trait_{index}": trait
            for index, trait in enumerate(traits, start=1)
        }
