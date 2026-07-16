"""Prompt package construction boundary for PersonaOS runtime intelligence."""

from typing import Any

from backend.models.prompt_package import PromptPackage
from backend.models.runtime_context import RuntimeContext


class PromptBuilder:
    """Converts RuntimeContext into a structured PromptPackage.

    The builder performs deterministic formatting only. It does not call model
    providers, optimize prompts, select adapters, persist data, or mutate
    engine-owned runtime records.
    """

    def build(
        self,
        runtime_context: RuntimeContext,
        user_input: str = "",
        conversation: list | None = None,
    ) -> PromptPackage:
        """Build a structured prompt package from prepared runtime context."""

        return PromptPackage(
            system=self._system_section(),
            persona=self._persona_section(runtime_context),
            memory=self._list_section(runtime_context, "memories"),
            knowledge=self._dict_section(runtime_context, "knowledge"),
            skills=self._list_section(runtime_context, "skills"),
            conversation=self._conversation_section(
                runtime_context,
                conversation,
            ),
            user_input=user_input,
            metadata=self._metadata_section(runtime_context),
        )

    def _system_section(self) -> dict:
        return {
            "boundary": "PromptBuilder",
            "responsibility": "deterministic runtime formatting",
            "provider_request": False,
        }

    def _persona_section(self, runtime_context: RuntimeContext) -> dict:
        return {
            "active_persona": self._get_value(
                runtime_context,
                "active_persona",
                None,
            ),
            "persona_version": self._get_value(
                runtime_context,
                "persona_version",
                "",
            )
            or "",
        }

    def _conversation_section(
        self,
        runtime_context: RuntimeContext,
        conversation: list | None,
    ) -> list:
        if conversation is not None:
            return conversation

        metadata = self._metadata_section(runtime_context)
        return metadata.get("conversation", []) or []

    def _metadata_section(self, runtime_context: RuntimeContext) -> dict:
        return self._get_value(runtime_context, "metadata", {}) or {}

    def _list_section(self, runtime_context: RuntimeContext, key: str) -> list:
        return self._get_value(runtime_context, key, []) or []

    def _dict_section(self, runtime_context: RuntimeContext, key: str) -> dict:
        return self._get_value(runtime_context, key, {}) or {}

    def _get_value(self, data: Any, key: str, default: Any) -> Any:
        if isinstance(data, dict):
            return data.get(key, default)

        return getattr(data, key, default)

