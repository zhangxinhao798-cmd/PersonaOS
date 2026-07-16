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
            relationship=self._relationship(context),
            memories=self._memories(context),
            knowledge=self._knowledge(context),
            skills=skills or [],
            confidence=self._get_value(context, "confidence", None),
            fusion_context=self._fusion_context(context),
            expression=self._expression(context),
            metadata=self._metadata(context, metadata),
        )

    def _memories(self, context: PersonaOSContext) -> list:
        memory_context = self._get_value(context, "memories", None)
        if memory_context is None:
            return []

        memories = self._get_value(memory_context, "memories", []) or []
        relevance = self._get_value(memory_context, "relevance", []) or []
        if not relevance:
            return memories

        return [
            {
                "content": self._get_value(memory, "content", ""),
                "category": self._get_value(memory, "category", ""),
                "source": self._get_value(memory, "source", ""),
                "confidence": self._get_value(memory, "confidence", 0.0),
                "importance": self._get_value(memory, "importance", 0.0),
                "timestamp": self._get_value(memory, "timestamp", ""),
                "relevance": relevance[index] if index < len(relevance) else {},
            }
            for index, memory in enumerate(memories)
        ]

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

    def _relationship(self, context: PersonaOSContext) -> dict:
        relationship_context = self._get_value(context, "relationship", None)
        if relationship_context is None:
            metadata = self._get_value(context, "metadata", {}) or {}
            relationship_context = metadata.get("relationship")

        if relationship_context is None:
            return {}

        if isinstance(relationship_context, dict):
            return dict(relationship_context)

        to_dict = getattr(relationship_context, "to_dict", None)
        if callable(to_dict):
            return to_dict()

        return {
            "relationship_type": self._get_value(
                relationship_context,
                "relationship_type",
                "",
            ),
            "interaction_style": self._get_value(
                relationship_context,
                "interaction_style",
                "",
            ),
            "tone": self._get_value(relationship_context, "tone", ""),
            "permissions": self._get_value(
                relationship_context,
                "permissions",
                [],
            )
            or [],
            "lifecycle": self._get_value(
                relationship_context,
                "lifecycle",
                "",
            ),
            "metadata": self._get_value(
                relationship_context,
                "metadata",
                {},
            )
            or {},
        }

    def _fusion_context(self, context: PersonaOSContext) -> list:
        fusion_memory = self._get_value(context, "fusion_memory", None)
        if fusion_memory is None:
            return []

        return self._get_value(fusion_memory, "fusions", []) or []

    def _expression(self, context: PersonaOSContext) -> dict:
        metadata = self._get_value(context, "metadata", {}) or {}
        expression = metadata.get("expression", {})
        if isinstance(expression, dict):
            return expression

        return {}

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
                "relationship": "PersonaOSContext.relationship",
                "memories": "PersonaOSContext.memories",
                "knowledge": "PersonaOSContext.knowledge",
                "skills": "external skill availability input",
                "confidence": "PersonaOSContext.confidence",
                "fusion_context": "PersonaOSContext.fusion_memory",
                "expression": "PersonaOSContext.metadata.expression",
                "memory_retrieval": "RuntimeMemoryRetriever read path",
            },
        )

        return runtime_metadata

    def _get_value(self, data: Any, key: str, default: Any) -> Any:
        if isinstance(data, dict):
            return data.get(key, default)

        return getattr(data, key, default)
