"""Runtime context assembly boundary for PersonaOS."""

from typing import Any

from backend.models.context import PersonaOSContext
from backend.models.runtime_context import RuntimeContext


class RuntimeContextAssembler:
    """Converts PersonaOS internal context into runtime-ready context.

    The assembler preserves source boundaries and does not own engine logic.
    Engine-owned retrieval, confidence evaluation, persona activation, and
    fusion interpretation must happen before data reaches this boundary.
    """

    def assemble(
        self,
        context: PersonaOSContext,
        skills: list | None = None,
        persona_version: str = "",
        metadata: dict | None = None,
    ) -> RuntimeContext:
        """Assemble a runtime-ready context from prepared component outputs."""

        return RuntimeContext(
            active_persona=self._get_value(context, "persona", None),
            persona_version=persona_version,
            memories=self._memories(context),
            knowledge=self._knowledge(context),
            skills=skills or [],
            confidence=self._get_value(context, "confidence", None),
            fusion_context=self._fusion_context(context),
            metadata=self._metadata(context, metadata),
        )

    def _memories(self, context: PersonaOSContext) -> list:
        memory_context = self._get_value(context, "memories", None)
        if memory_context is None:
            return []

        return self._get_value(memory_context, "memories", []) or []

    def _knowledge(self, context: PersonaOSContext) -> dict:
        knowledge_context = self._get_value(context, "knowledge", None)
        if knowledge_context is None:
            return {
                "records": [],
                "sources": [],
            }

        return {
            "records": (
                self._get_value(
                    knowledge_context,
                    "knowledge_records",
                    [],
                )
                or []
            ),
            "sources": self._get_value(knowledge_context, "sources", []) or [],
        }

    def _fusion_context(self, context: PersonaOSContext) -> list:
        fusion_memory = self._get_value(context, "fusion_memory", None)
        if fusion_memory is None:
            return []

        return self._get_value(fusion_memory, "fusions", []) or []

    def _metadata(
        self,
        context: PersonaOSContext,
        metadata: dict | None,
    ) -> dict:
        runtime_metadata = dict(metadata or {})
        runtime_metadata.setdefault(
            "query",
            self._get_value(context, "query", ""),
        )
        runtime_metadata.setdefault(
            "source_boundaries",
            {
                "active_persona": "PersonaOSContext.persona",
                "memories": "PersonaOSContext.memories",
                "knowledge": "PersonaOSContext.knowledge",
                "skills": "external skill availability input",
                "confidence": "PersonaOSContext.confidence",
                "fusion_context": "PersonaOSContext.fusion_memory",
            },
        )

        return runtime_metadata

    def _get_value(self, data: Any, key: str, default: Any) -> Any:
        if isinstance(data, dict):
            return data.get(key, default)

        return getattr(data, key, default)
