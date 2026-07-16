"""Tests for Persistence Architecture v1 repository boundaries."""

import copy
import inspect

from backend.core.knowledge import KnowledgeRecord
from backend.models.memory_record import MemoryRecord
from backend.repositories import (
    InMemoryKnowledgeRepository,
    InMemoryMemoryRepository,
    InMemoryPersonaRepository,
)

from tests.test_session_manager import make_entry


def make_memory() -> MemoryRecord:
    return MemoryRecord(
        content="User likes careful architecture.",
        category="preference",
        confidence=0.8,
        importance=0.7,
        source="test",
        timestamp="2026-07-16T00:00:00Z",
    )


def make_knowledge() -> KnowledgeRecord:
    return KnowledgeRecord(
        content="Repositories isolate business logic from storage.",
        category="architecture",
        source="docs/ARCHITECTURE_PRINCIPLES.md",
        confidence=0.9,
        timestamp="2026-07-16T00:00:00Z",
    )


def test_memory_repository_save_retrieve_list_and_delete() -> None:
    repository = InMemoryMemoryRepository()
    memory = make_memory()

    repository.save("memory-1", memory)

    assert repository.get("memory-1") is memory
    assert repository.list() == [memory]
    assert repository.delete("memory-1") is True
    assert repository.delete("memory-1") is False
    assert repository.get("memory-1") is None


def test_memory_repository_does_not_mutate_memory_record() -> None:
    repository = InMemoryMemoryRepository()
    memory = make_memory()
    before = copy.deepcopy(memory.__dict__)

    repository.save("memory-1", memory)
    repository.get("memory-1")
    repository.list()

    assert memory.__dict__ == before


def test_persona_repository_save_retrieve_list_and_delete() -> None:
    repository = InMemoryPersonaRepository()
    entry = make_entry()

    repository.save(entry)

    assert repository.get(entry.id) is entry
    assert repository.list() == [entry]
    assert repository.delete(entry.id) is True
    assert repository.delete(entry.id) is False
    assert repository.get(entry.id) is None


def test_persona_repository_does_not_modify_profile_or_versions() -> None:
    repository = InMemoryPersonaRepository()
    entry = make_entry()
    profile_before = copy.deepcopy(entry.profile.__dict__)
    versions_before = copy.deepcopy([version.__dict__ for version in entry.versions])

    repository.save(entry)
    repository.get(entry.id)
    repository.list()

    assert entry.profile.__dict__ == profile_before
    assert [version.__dict__ for version in entry.versions] == versions_before


def test_knowledge_repository_save_retrieve_list_and_delete() -> None:
    repository = InMemoryKnowledgeRepository()
    knowledge = make_knowledge()

    repository.save("knowledge-1", knowledge)

    assert repository.get("knowledge-1") is knowledge
    assert repository.list() == [knowledge]
    assert repository.delete("knowledge-1") is True
    assert repository.delete("knowledge-1") is False
    assert repository.get("knowledge-1") is None


def test_knowledge_repository_does_not_mutate_record() -> None:
    repository = InMemoryKnowledgeRepository()
    knowledge = make_knowledge()
    before = copy.deepcopy(knowledge.__dict__)

    repository.save("knowledge-1", knowledge)
    repository.get("knowledge-1")
    repository.list()

    assert knowledge.__dict__ == before


def test_repositories_do_not_import_core_engines_or_databases() -> None:
    import backend.repositories.knowledge_repository as knowledge_repository
    import backend.repositories.memory_repository as memory_repository
    import backend.repositories.persona_repository as persona_repository

    source = "\n".join(
        [
            inspect.getsource(memory_repository),
            inspect.getsource(persona_repository),
            inspect.getsource(knowledge_repository),
        ]
    ).lower()

    assert "memoryengine" not in source
    assert "personaengine" not in source
    assert "knowledgeengine" not in source
    assert "sqlite" not in source
    assert "postgres" not in source
    assert "database" not in source
