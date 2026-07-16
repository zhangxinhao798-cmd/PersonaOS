"""Shared context boundary models for PersonaOS orchestration."""

from dataclasses import dataclass, field

from backend.models.fusion import FusionContext


@dataclass
class PersonaContext:
    """Structured persona data prepared for orchestration."""

    name: str = ""
    traits: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    style: str = ""


@dataclass
class MemoryContext:
    """Experience-derived context prepared for orchestration."""

    memories: list = field(default_factory=list)
    relevance: list[dict] = field(default_factory=list)


@dataclass
class FusionMemoryContext:
    """Persona-aware memory interpretations prepared for orchestration."""

    fusions: list[FusionContext] = field(default_factory=list)


@dataclass
class KnowledgeContext:
    """Source-backed knowledge prepared for orchestration."""

    knowledge_records: list = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass
class ConfidenceContext:
    """Reliability assessment data prepared for orchestration."""

    score: float = 0.0
    factors: dict = field(default_factory=dict)


@dataclass
class PersonaOSContext:
    """Shared communication format between engines and the orchestrator."""

    query: str = ""
    persona: PersonaContext = field(default_factory=PersonaContext)
    memories: MemoryContext = field(default_factory=MemoryContext)
    fusion_memory: FusionMemoryContext = field(
        default_factory=FusionMemoryContext
    )
    knowledge: KnowledgeContext = field(default_factory=KnowledgeContext)
    confidence: ConfidenceContext = field(default_factory=ConfidenceContext)
