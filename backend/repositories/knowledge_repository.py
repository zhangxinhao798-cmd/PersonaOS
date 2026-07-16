"""Knowledge repository boundary for PersonaOS."""

from typing import Protocol

from backend.core.knowledge import KnowledgeRecord


class KnowledgeRepository(Protocol):
    """Storage boundary for knowledge records."""

    def save(self, record_id: str, record: KnowledgeRecord) -> None:
        """Save or replace a knowledge record."""

    def get(self, record_id: str) -> KnowledgeRecord | None:
        """Return a knowledge record by id."""

    def list(self) -> list[KnowledgeRecord]:
        """Return all knowledge records."""

    def delete(self, record_id: str) -> bool:
        """Delete a knowledge record and return whether one was removed."""


class InMemoryKnowledgeRepository:
    """In-memory KnowledgeRepository implementation.

    This repository does not fetch, crawl, vectorize, or rank knowledge. It
    only stores records explicitly handed to it.
    """

    def __init__(self) -> None:
        self._records: dict[str, KnowledgeRecord] = {}

    def save(self, record_id: str, record: KnowledgeRecord) -> None:
        self._records[record_id] = record

    def get(self, record_id: str) -> KnowledgeRecord | None:
        return self._records.get(record_id)

    def list(self) -> list[KnowledgeRecord]:
        return list(self._records.values())

    def delete(self, record_id: str) -> bool:
        if record_id not in self._records:
            return False

        del self._records[record_id]
        return True

