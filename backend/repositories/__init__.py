"""Repository boundaries for PersonaOS storage implementations."""

from backend.repositories.knowledge_repository import (
    InMemoryKnowledgeRepository,
    KnowledgeRepository,
)
from backend.repositories.memory_repository import (
    InMemoryMemoryRepository,
    MemoryRepository,
)
from backend.repositories.persona_repository import (
    InMemoryPersonaRepository,
    PersonaRepository,
)

