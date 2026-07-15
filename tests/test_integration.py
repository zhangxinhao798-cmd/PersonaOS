"""Integration tests for PersonaOS orchestration."""

from backend.core.confidence import ConfidenceEngine
from backend.core.evolution import EvolutionEngine
from backend.core.knowledge import KnowledgeEngine, KnowledgeRecord
from backend.core.memory import MemoryEngine
from backend.core.persona import PersonaEngine
from backend.core.skill import SkillEngine
from backend.engine.context_builder import ContextBuilder
from backend.engine.persona_os import PersonaOS
from backend.fusion import PersonaMemoryFusion
from backend.models.context import PersonaOSContext
from backend.models.memory_record import MemoryRecord


def make_memory(content: str) -> MemoryRecord:
    return MemoryRecord(
        content=content,
        category="semantic",
        confidence=0.8,
        importance=0.7,
        source="test",
        timestamp="2026-07-15T00:00:00Z",
    )


def make_knowledge(content: str) -> KnowledgeRecord:
    return KnowledgeRecord(
        content=content,
        category="investment",
        source="test-source",
        confidence=0.9,
        timestamp="2026-07-15T00:00:00Z",
    )


def test_persona_os_initialization() -> None:
    persona_os = PersonaOS()

    assert isinstance(persona_os.persona_engine, PersonaEngine)
    assert isinstance(persona_os.memory_engine, MemoryEngine)
    assert isinstance(persona_os.persona_memory_fusion, PersonaMemoryFusion)
    assert isinstance(persona_os.knowledge_engine, KnowledgeEngine)
    assert isinstance(persona_os.skill_engine, SkillEngine)
    assert isinstance(persona_os.confidence_engine, ConfidenceEngine)
    assert isinstance(persona_os.evolution_engine, EvolutionEngine)
    assert isinstance(persona_os.context_builder, ContextBuilder)


def test_process_context_returns_context() -> None:
    context = PersonaOS().process_context("test query")

    assert isinstance(context, PersonaOSContext)
    assert context.persona is not None
    assert context.memories is not None
    assert context.fusion_memory is not None
    assert context.knowledge is not None
    assert context.confidence is not None


def test_confidence_engine_boundary() -> None:
    class RecordingConfidenceEngine(ConfidenceEngine):
        def __init__(self) -> None:
            super().__init__()
            self.evaluate_called = False

        def evaluate(
            self,
            memories: list[MemoryRecord],
            knowledge_records: list | None = None,
        ) -> dict:
            self.evaluate_called = True
            return {
                "score": 0.42,
                "factors": {
                    "memory_count": len(memories),
                    "knowledge_count": len(knowledge_records or []),
                },
            }

    confidence_engine = RecordingConfidenceEngine()
    persona_os = PersonaOS(confidence_engine=confidence_engine)

    context = persona_os.process_context("test query")

    assert confidence_engine.evaluate_called
    assert context.confidence.score == 0.42
    assert not hasattr(persona_os, "_build_confidence_data")


def test_empty_context_handling() -> None:
    context = PersonaOS().process_context("no matching information")

    assert isinstance(context, PersonaOSContext)
    assert context.memories.memories == []
    assert context.knowledge.knowledge_records == []
    assert context.confidence.score == 0.0


def test_orchestration_flow() -> None:
    calls = []

    class RecordingPersonaEngine(PersonaEngine):
        def get_profile(self):
            calls.append("persona")
            return super().get_profile()

    class RecordingMemoryEngine(MemoryEngine):
        def retrieve_memory(
            self,
            category: str | None = None,
            source: str | None = None,
            minimum_confidence: float | None = None,
            minimum_importance: float | None = None,
        ) -> list[MemoryRecord]:
            calls.append("memory")
            return super().retrieve_memory(
                category=category,
                source=source,
                minimum_confidence=minimum_confidence,
                minimum_importance=minimum_importance,
            )

    class RecordingKnowledgeEngine(KnowledgeEngine):
        def retrieve_knowledge(self, query: str) -> list[KnowledgeRecord]:
            calls.append("knowledge")
            return super().retrieve_knowledge(query)

    class RecordingPersonaMemoryFusion(PersonaMemoryFusion):
        def fuse(self, persona, memory):
            calls.append("fusion")
            return super().fuse(persona, memory)

    class RecordingConfidenceEngine(ConfidenceEngine):
        def evaluate(
            self,
            memories: list[MemoryRecord],
            knowledge_records: list | None = None,
        ) -> dict:
            calls.append("confidence")
            return super().evaluate(memories, knowledge_records)

    class RecordingContextBuilder(ContextBuilder):
        def build_context(
            self,
            query,
            persona_data,
            memories,
            knowledge_records,
            confidence_data,
            fusions=None,
        ) -> PersonaOSContext:
            calls.append("context_builder")
            return super().build_context(
                query=query,
                persona_data=persona_data,
                memories=memories,
                knowledge_records=knowledge_records,
                confidence_data=confidence_data,
                fusions=fusions,
            )

    memory_engine = RecordingMemoryEngine()
    memory_engine.create_memory(
        make_memory("Investment analysis should consider company fundamentals.")
    )

    knowledge_engine = RecordingKnowledgeEngine()
    knowledge_engine.create_knowledge(
        make_knowledge("Company investment analysis uses source-backed data.")
    )

    persona_os = PersonaOS(
        persona_engine=RecordingPersonaEngine(),
        memory_engine=memory_engine,
        persona_memory_fusion=RecordingPersonaMemoryFusion(),
        knowledge_engine=knowledge_engine,
        confidence_engine=RecordingConfidenceEngine(),
        context_builder=RecordingContextBuilder(),
    )

    context = persona_os.process_context("Analyze a company investment")

    assert isinstance(context, PersonaOSContext)
    assert calls == [
        "persona",
        "memory",
        "fusion",
        "knowledge",
        "confidence",
        "context_builder",
    ]
    assert len(context.memories.memories) == 1
    assert len(context.fusion_memory.fusions) == 1
    assert len(context.knowledge.knowledge_records) == 1
