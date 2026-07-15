"""Top-level PersonaOS backend orchestrator."""

from backend.core.confidence import ConfidenceEngine
from backend.core.evolution import EvolutionEngine
from backend.core.knowledge import KnowledgeEngine
from backend.core.memory import MemoryEngine
from backend.core.persona import PersonaEngine
from backend.core.skill import SkillEngine


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
    ) -> None:
        self.persona_engine = persona_engine or PersonaEngine()
        self.memory_engine = memory_engine or MemoryEngine()
        self.knowledge_engine = knowledge_engine or KnowledgeEngine()
        self.skill_engine = skill_engine or SkillEngine()
        self.confidence_engine = confidence_engine or ConfidenceEngine()
        self.evolution_engine = evolution_engine or EvolutionEngine()

