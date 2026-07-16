"""Prompt rendering boundary for PersonaOS runtime intelligence."""

import json
from typing import Any

from backend.models.final_prompt import FinalPrompt
from backend.models.prompt_package import PromptPackage


class PromptRenderer:
    """Converts a PromptPackage into deterministic rendered prompt text.

    The renderer performs formatting only. It does not optimize prompts, count
    tokens, call providers, make HTTP requests, or orchestrate runtime flow.
    """

    def render(self, prompt_package: PromptPackage) -> FinalPrompt:
        """Render a prompt package while preserving section ordering."""

        sections = [
            self._render_section(name, value)
            for name, value in prompt_package.ordered_sections()
        ]

        return FinalPrompt(
            text="\n\n".join(sections),
            metadata=prompt_package.metadata or {},
        )

    def _render_section(self, name: str, value: Any) -> str:
        return f"## {self._section_title(name)}\n{self._render_value(value)}"

    def _section_title(self, name: str) -> str:
        return name.replace("_", " ").title()

    def _render_value(self, value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, str):
            return value

        if isinstance(value, (dict, list, tuple)):
            return json.dumps(
                value,
                default=str,
                indent=2,
                sort_keys=True,
            )

        return str(value)

