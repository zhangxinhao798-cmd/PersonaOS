"""Context builder layer for PersonaOS orchestration."""

from typing import Any

from backend.models.context import (
    ConfidenceContext,
    KnowledgeContext,
    MemoryContext,
    PersonaContext,
    PersonaOSContext,
)


class ContextBuilder:
    """Converts engine outputs into a shared PersonaOS context."""

    def build_context(
        self,
        query: str,
        persona_data: Any,
        memories: list,
        knowledge_records: list,
        confidence_data: Any,
    ) -> PersonaOSContext:
        """Build a PersonaOSContext from already-prepared engine outputs."""

        return PersonaOSContext(
            query=query,
            persona=self._build_persona_context(persona_data),
            memories=MemoryContext(memories=memories),
            knowledge=KnowledgeContext(
                knowledge_records=knowledge_records,
                sources=self._extract_sources(knowledge_records),
            ),
            confidence=self._build_confidence_context(confidence_data),
        )

    def _build_persona_context(self, persona_data: Any) -> PersonaContext:
        return PersonaContext(
            name=self._get_value(persona_data, "name", ""),
            traits=self._as_trait_list(
                self._get_value(persona_data, "traits", [])
            ),
            values=self._get_value(persona_data, "values", []),
            style=self._get_value(persona_data, "style", ""),
        )

    def _build_confidence_context(
        self,
        confidence_data: Any,
    ) -> ConfidenceContext:
        return ConfidenceContext(
            score=self._get_value(confidence_data, "score", 0.0),
            factors=self._get_value(confidence_data, "factors", {}),
        )

    def _extract_sources(self, knowledge_records: list) -> list[str]:
        return [
            source
            for record in knowledge_records
            if (source := self._get_value(record, "source", None)) is not None
        ]

    def _get_value(self, data: Any, key: str, default: Any) -> Any:
        if isinstance(data, dict):
            return data.get(key, default)

        return getattr(data, key, default)

    def _as_trait_list(self, traits: Any) -> list[str]:
        if isinstance(traits, dict):
            return [
                f"{name}: {value}"
                for name, value in traits.items()
            ]

        return traits
