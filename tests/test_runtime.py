"""Runtime initialization tests for PersonaOS."""

from backend.core.confidence import ConfidenceEngine
from backend.core.evolution import EvolutionEngine
from backend.core.knowledge import KnowledgeEngine
from backend.core.memory import MemoryEngine
from backend.core.persona import PersonaEngine
from backend.core.skill import SkillEngine
from backend.engine.persona_os import PersonaOS
from backend.main import create_app


def test_persona_os_runtime_initializes_core_engines() -> None:
    """PersonaOS should boot with each modular engine available."""

    app = create_app()

    assert isinstance(app, PersonaOS)
    assert isinstance(app.persona_engine, PersonaEngine)
    assert isinstance(app.memory_engine, MemoryEngine)
    assert isinstance(app.knowledge_engine, KnowledgeEngine)
    assert isinstance(app.skill_engine, SkillEngine)
    assert isinstance(app.confidence_engine, ConfidenceEngine)
    assert isinstance(app.evolution_engine, EvolutionEngine)
