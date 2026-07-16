"""Controlled chat runtime boundary for PersonaOS."""

from backend.adapters.llm import BaseLLMAdapter
from backend.core.persona_selector import PersonaSelector
from backend.engine.runtime_context_assembler import RuntimeContextAssembler
from backend.models.context import PersonaOSContext
from backend.models.llm_response import LLMResponse
from backend.models.persona_library import PersonaLibraryEntry


class ChatRuntimeError(Exception):
    """Base error for controlled chat runtime failures."""


class EmptyUserInputError(ChatRuntimeError):
    """Raised when a runtime turn receives empty user input."""


class PersonaNotSelectableError(ChatRuntimeError):
    """Raised when persona selection is blocked by lifecycle rules."""


class PersonaInactiveError(PersonaNotSelectableError):
    """Raised when a persona is approved but not active."""


class InvalidPersonaVersionError(PersonaNotSelectableError):
    """Raised when a persona lacks a valid current version."""


class AdapterUnavailableError(ChatRuntimeError):
    """Raised when no configured adapter is available."""


class AdapterGenerationError(ChatRuntimeError):
    """Raised when adapter generation fails behind the runtime boundary."""


class ChatRuntime:
    """Coordinate one controlled user-message generation turn.

    ChatRuntime validates persona selection, assembles RuntimeContext, and
    delegates generation to the configured adapter. It does not own persona
    lifecycle rules, prompt formatting, provider transport, or durable state.
    """

    def __init__(
        self,
        persona_selector: PersonaSelector,
        adapter: BaseLLMAdapter | None,
        runtime_context_assembler: RuntimeContextAssembler | None = None,
    ) -> None:
        self.persona_selector = persona_selector
        self.adapter = adapter
        self.runtime_context_assembler = (
            runtime_context_assembler or RuntimeContextAssembler()
        )

    def generate_reply(
        self,
        user_input: str,
        persona_entry: PersonaLibraryEntry,
        persona_os_context: PersonaOSContext,
    ) -> LLMResponse:
        """Generate a reply through the controlled runtime boundary."""

        cleaned_input = self._validate_user_input(user_input)
        selected_persona = self._select_persona(persona_entry)

        if self.adapter is None:
            raise AdapterUnavailableError("No LLM adapter is configured.")

        metadata = dict(getattr(persona_os_context, "metadata", {}) or {})
        metadata.update(
            {
                "persona_entry_id": selected_persona.id,
                "persona_version_id": selected_persona.current_version_id,
            }
        )

        runtime_context = self.runtime_context_assembler.assemble(
            persona_os_context,
            persona_version=selected_persona.current_version_id,
            metadata=metadata,
        )

        try:
            return self.adapter.generate(runtime_context, cleaned_input)
        except ChatRuntimeError:
            raise
        except Exception as exc:
            raise AdapterGenerationError("Adapter generation failed.") from exc

    def _validate_user_input(self, user_input: str) -> str:
        if not isinstance(user_input, str) or not user_input.strip():
            raise EmptyUserInputError("User input is required.")

        return user_input

    def _select_persona(
        self,
        persona_entry: PersonaLibraryEntry,
    ) -> PersonaLibraryEntry:
        selected_persona = self.persona_selector.select(persona_entry.id)
        if selected_persona is not None:
            return selected_persona

        if not persona_entry.is_approved_for_activation():
            raise PersonaNotSelectableError("Persona is not selectable.")
        if not persona_entry.is_active():
            raise PersonaInactiveError("Persona is not active.")
        if not persona_entry.has_valid_current_version():
            raise InvalidPersonaVersionError(
                "Persona current version is missing or invalid."
            )

        raise PersonaNotSelectableError("Persona is not selectable.")
