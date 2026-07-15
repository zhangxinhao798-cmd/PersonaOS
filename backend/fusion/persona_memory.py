"""Persona-memory fusion coordination layer."""

from typing import Any

from backend.models.fusion import FusionContext


class PersonaMemoryFusion:
    """Builds persona-aware interpretations of memory records."""

    def fuse(self, persona: Any, memory: Any) -> FusionContext:
        """Return deterministic persona-aware context for one memory."""

        persona_name = self._get_value(persona, "name", "")
        memory_content = self._get_value(memory, "content", "")
        persona_tokens = self._persona_tokens(persona)
        memory_tokens = self._memory_tokens(memory)
        matched_tokens = persona_tokens & memory_tokens

        relevance_score = self._calculate_relevance(
            matched_tokens,
            persona_tokens,
        )
        confidence = self._calculate_confidence(memory, relevance_score)

        return FusionContext(
            memory_id=self._memory_id(memory),
            memory_content=memory_content,
            persona_name=persona_name,
            interpretation=self._interpret(
                persona_name,
                matched_tokens,
                relevance_score,
            ),
            relevance_score=relevance_score,
            confidence=confidence,
        )

    def _persona_tokens(self, persona: Any) -> set[str]:
        traits = self._get_value(persona, "traits", {})
        values = self._get_value(persona, "values", [])
        text_parts = []

        if isinstance(traits, dict):
            for name, value in traits.items():
                text_parts.extend([str(name), str(value)])
        else:
            text_parts.extend(str(trait) for trait in traits)

        text_parts.extend(str(value) for value in values)

        return self._tokenize(" ".join(text_parts))

    def _memory_tokens(self, memory: Any) -> set[str]:
        content = self._get_value(memory, "content", "")
        category = self._get_value(memory, "category", "")

        return self._tokenize(f"{content} {category}")

    def _calculate_relevance(
        self,
        matched_tokens: set[str],
        persona_tokens: set[str],
    ) -> float:
        if not persona_tokens:
            return 0.0

        return self._clamp(len(matched_tokens) / len(persona_tokens))

    def _calculate_confidence(
        self,
        memory: Any,
        relevance_score: float,
    ) -> float:
        memory_confidence = self._get_value(memory, "confidence", 0.0)

        return self._clamp((memory_confidence + relevance_score) / 2)

    def _interpret(
        self,
        persona_name: str,
        matched_tokens: set[str],
        relevance_score: float,
    ) -> str:
        if not matched_tokens:
            return "No direct persona-memory alignment found."

        matches = ", ".join(sorted(matched_tokens))
        return (
            f"Memory aligns with {persona_name or 'persona'} through "
            f"{matches} with relevance {relevance_score:.2f}."
        )

    def _memory_id(self, memory: Any) -> str:
        memory_id = self._get_value(memory, "memory_id", None)
        if memory_id is None:
            memory_id = self._get_value(memory, "id", None)
        if memory_id is None:
            memory_id = id(memory)

        return str(memory_id)

    def _get_value(self, data: Any, key: str, default: Any) -> Any:
        if isinstance(data, dict):
            return data.get(key, default)

        return getattr(data, key, default)

    def _tokenize(self, text: str) -> set[str]:
        punctuation = ".,!?;:()[]{}\"'"
        return {
            word.strip(punctuation).lower()
            for word in text.split()
            if word.strip(punctuation)
        }

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))
