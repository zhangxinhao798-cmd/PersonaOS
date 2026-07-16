"""Memory repository boundary for PersonaOS."""

from typing import Protocol

from backend.models.memory_record import MemoryRecord


class MemoryRepository(Protocol):
    """Storage boundary for memory records."""

    def save(self, record_id: str, record: MemoryRecord) -> None:
        """Save or replace a memory record."""

    def get(self, record_id: str) -> MemoryRecord | None:
        """Return a memory record by id."""

    def list(self) -> list[MemoryRecord]:
        """Return all memory records."""

    def delete(self, record_id: str) -> bool:
        """Delete a memory record and return whether one was removed."""


class InMemoryMemoryRepository:
    """In-memory MemoryRepository implementation.

    This repository does not generate, summarize, or mutate memories. It only
    stores records explicitly handed to it.
    """

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}

    def save(self, record_id: str, record: MemoryRecord) -> None:
        self._records[record_id] = record

    def get(self, record_id: str) -> MemoryRecord | None:
        return self._records.get(record_id)

    def list(self) -> list[MemoryRecord]:
        return list(self._records.values())

    def delete(self, record_id: str) -> bool:
        if record_id not in self._records:
            return False

        del self._records[record_id]
        return True

