"""Top-level PersonaOS backend orchestrator."""

from backend.core.confidence import ConfidenceEngine
from backend.core.evolution import EvolutionEngine
from backend.core.knowledge import KnowledgeEngine
from backend.core.memory import MemoryEngine
from backend.core.persona import PersonaEngine
from backend.core.skill import SkillEngine
from backend.engine.context_builder import ContextBuilder
from backend.models.context import PersonaOSContext


class PersonaOS:
    """Composes the modular engines that make up PersonaOS.

    This class is the initial backend assembly point. It should coordinate
    engines without collapsing their responsibilities into a monolith.
    """

    def __init__(
        self,
        persona_engine: PersonaEngine | None = None,
        memory_engine: MemoryEngine | None = None,
        knowledge_engine: KnowledgeEngine | None = None,
        skill_engine: SkillEngine | None = None,
        confidence_engine: ConfidenceEngine | None = None,
        evolution_engine: EvolutionEngine | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self.persona_engine = persona_engine or PersonaEngine()
        self.memory_engine = memory_engine or MemoryEngine()
        self.knowledge_engine = knowledge_engine or KnowledgeEngine()
        self.skill_engine = skill_engine or SkillEngine()
        self.confidence_engine = confidence_engine or ConfidenceEngine()
        self.evolution_engine = evolution_engine or EvolutionEngine()
        self.context_builder = context_builder or ContextBuilder()

    def process_context(self, query: str) -> PersonaOSContext:
        """Coordinate engines and return the shared operating context."""

        persona_data = self.persona_engine.get_profile()
        memories = self.memory_engine.retrieve_memory()
        knowledge_records = self.knowledge_engine.retrieve_knowledge(query)
        confidence_data = self.confidence_engine.evaluate(
            memories,
            knowledge_records,
        )

        return self.context_builder.build_context(
            query=query,
            persona_data=persona_data,
            memories=memories,
            knowledge_records=knowledge_records,
            confidence_data=confidence_data,
        )
