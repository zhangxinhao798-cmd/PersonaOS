"""Shared schema placeholders for PersonaOS.

These classes define early architectural boundaries for data passed between
engines. Fields and validation rules will be added when implementation begins.
"""


class PersonaContext:
    """Represents the active persona operating context."""

    pass


class MemoryRecord:
    """Represents an experience-derived memory record."""

    pass


class KnowledgeRecord:
    """Represents source-backed knowledge."""

    pass


class SkillDescriptor:
    """Represents metadata for a governed capability."""

    pass


class ConfidenceAssessment:
    """Represents reliability-awareness guidance."""

    pass


class EvolutionProposal:
    """Represents a proposed durable change."""

    pass

