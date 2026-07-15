"""Persona Importer boundary for PersonaOS."""

from typing import Any

from backend.models.persona_import import PersonaImportResult
from backend.models.persona_source import PersonaSource


class PersonaImporter:
    """Creates persona import results from external persona sources.

    The importer is deterministic and rule-based. It does not call model
    providers, persist data, create embeddings, or activate personas.
    """

    def import_persona(
        self,
        source: PersonaSource,
    ) -> PersonaImportResult:
        """Return a structured import result for a persona source."""

        metadata = source.metadata or {}
        content_fields = self._extract_content_fields(source.content)

        return PersonaImportResult(
            source_id=source.id,
            persona_name=self._first_text(
                metadata.get("persona_name"),
                metadata.get("name"),
                source.name,
            ),
            traits=self._field_values(metadata, content_fields, "traits"),
            values=self._field_values(metadata, content_fields, "values"),
            thinking_patterns=self._field_values(
                metadata,
                content_fields,
                "thinking_patterns",
            ),
            communication_style=self._field_values(
                metadata,
                content_fields,
                "communication_style",
            ),
            confidence=self._confidence(metadata.get("confidence")),
        )

    def _field_values(
        self,
        metadata: dict,
        content_fields: dict[str, list[str]],
        key: str,
    ) -> list[str]:
        values = self._as_list(metadata.get(key))
        values.extend(content_fields.get(key, []))
        return values

    def _extract_content_fields(self, content: str) -> dict[str, list[str]]:
        fields = {
            "traits": [],
            "values": [],
            "thinking_patterns": [],
            "communication_style": [],
        }
        prefixes = {
            "trait": "traits",
            "traits": "traits",
            "value": "values",
            "values": "values",
            "thinking": "thinking_patterns",
            "thinking_pattern": "thinking_patterns",
            "thinking_patterns": "thinking_patterns",
            "style": "communication_style",
            "communication_style": "communication_style",
        }

        for line in content.splitlines():
            if ":" not in line:
                continue

            label, value = line.split(":", 1)
            key = prefixes.get(label.strip().lower())
            if key is None:
                continue

            fields[key].extend(self._split_values(value))

        return fields

    def _as_list(self, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(item) for item in value if str(item)]

        return self._split_values(str(value))

    def _split_values(self, value: str) -> list[str]:
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    def _first_text(self, *values: Any) -> str:
        for value in values:
            if value is None:
                continue

            text = str(value)
            if text:
                return text

        return ""

    def _confidence(self, value: Any) -> float:
        if value is None:
            return 0.0

        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
