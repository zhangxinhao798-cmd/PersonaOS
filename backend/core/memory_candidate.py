"""Deterministic memory candidate extraction and review queue."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import re

from backend.models.memory_candidate import MemoryCandidate


class MemoryCandidateError(Exception):
    """Base error for memory candidate review failures."""


class MemoryCandidateNotFoundError(MemoryCandidateError):
    """Raised when a candidate cannot be found in the review queue."""


class DuplicateMemoryCandidateError(MemoryCandidateError):
    """Raised when a duplicate candidate is added explicitly."""


class CandidateExtractor:
    """Deterministic, rule-based memory candidate extractor.

    This extractor is deliberately simple. It does not call an LLM, summarize
    conversation, approve candidates, or create durable memory.
    """

    RULES: tuple[tuple[str, str, str, float, str, float], ...] = (
        (
            "user_preference",
            r"\b(?:i prefer|i like|i love|i enjoy)\s+(.+)",
            "User stated a possible stable preference.",
            0.8,
            "semantic",
            0.8,
        ),
        (
            "long_term_goal",
            r"\b(?:my goal is|i want to|i plan to|i hope to)\s+(.+)",
            "User stated a possible long-term goal.",
            0.75,
            "semantic",
            0.85,
        ),
        (
            "explicit_personal_fact",
            r"\b(?:my name is|i am|i live in|i work as)\s+(.+)",
            "User stated an explicit personal fact.",
            0.85,
            "semantic",
            0.75,
        ),
        (
            "stable_habit",
            r"\b(?:i usually|i always|i often)\s+(.+)",
            "User stated a possible stable habit.",
            0.7,
            "procedural",
            0.7,
        ),
    )

    def extract(self, source_turn: dict | object) -> list[MemoryCandidate]:
        """Extract reviewable candidates from one conversation turn."""

        turn = self._turn_to_dict(source_turn)
        if turn.get("role") != "user":
            return []

        content = str(turn.get("content", "")).strip()
        if not content:
            return []

        candidates = []
        for (
            candidate_type,
            pattern,
            reason,
            confidence,
            category,
            importance,
        ) in self.RULES:
            match = re.search(pattern, content, re.IGNORECASE)
            if not match:
                continue

            extracted = self._clean_content(match.group(1))
            if not extracted:
                continue

            candidate_content = self._candidate_content(
                candidate_type,
                extracted,
            )
            candidates.append(
                MemoryCandidate(
                    id=self._candidate_id(
                        candidate_type,
                        candidate_content,
                        content,
                    ),
                    source_turn=turn,
                    candidate_type=candidate_type,
                    content=candidate_content,
                    confidence=confidence,
                    reason=reason,
                    category=category,
                    importance=importance,
                    metadata={
                        "extractor": "CandidateExtractor",
                        "rule": candidate_type,
                        "automatic_persistence": False,
                    },
                    created_at=str(turn.get("created_at", "") or ""),
                )
            )

        return self._deduplicate(candidates)

    def _turn_to_dict(self, source_turn: dict | object) -> dict:
        if isinstance(source_turn, dict):
            return dict(source_turn)
        if hasattr(source_turn, "to_dict"):
            return dict(source_turn.to_dict())

        return {
            "role": getattr(source_turn, "role", ""),
            "content": getattr(source_turn, "content", ""),
            "created_at": getattr(source_turn, "created_at", ""),
            "metadata": dict(getattr(source_turn, "metadata", {}) or {}),
        }

    def _clean_content(self, content: str) -> str:
        return content.strip().strip(".!?;: ")

    def _candidate_content(self, candidate_type: str, extracted: str) -> str:
        prefixes = {
            "user_preference": "User prefers",
            "long_term_goal": "User wants to",
            "explicit_personal_fact": "User stated",
            "stable_habit": "User often",
        }
        return f"{prefixes[candidate_type]} {extracted}."

    def _candidate_id(
        self,
        candidate_type: str,
        candidate_content: str,
        source_content: str,
    ) -> str:
        raw = f"{candidate_type}|{candidate_content}|{source_content}".lower()
        digest = sha256(raw.encode("utf-8")).hexdigest()[:16]
        return f"memory-candidate-{digest}"

    def _deduplicate(
        self,
        candidates: list[MemoryCandidate],
    ) -> list[MemoryCandidate]:
        seen = set()
        unique = []
        for candidate in candidates:
            key = (candidate.candidate_type, candidate.content.lower())
            if key in seen:
                continue
            seen.add(key)
            unique.append(candidate)

        return unique


@dataclass
class ReviewQueue:
    """In-memory review queue for memory candidates.

    Approval and rejection only update candidate review state. The queue does
    not write MemoryEngine, repositories, databases, or vector stores.
    """

    candidates: dict[str, MemoryCandidate] = field(default_factory=dict)

    def add(self, candidate: MemoryCandidate) -> MemoryCandidate:
        """Add one candidate if it is not already queued."""

        duplicate = self._find_duplicate(candidate)
        if duplicate is not None:
            return duplicate

        self.candidates[candidate.id] = candidate
        return candidate

    def add_many(
        self,
        candidates: list[MemoryCandidate],
    ) -> list[MemoryCandidate]:
        """Add many candidates with duplicate suppression."""

        return [self.add(candidate) for candidate in candidates]

    def list_candidates(
        self,
        status: str | None = None,
    ) -> list[MemoryCandidate]:
        """List queued candidates, optionally filtered by review status."""

        values = list(self.candidates.values())
        if status is None:
            return values

        return [
            candidate
            for candidate in values
            if candidate.review_status == status
        ]

    def get(self, candidate_id: str) -> MemoryCandidate:
        """Return one candidate by id."""

        if candidate_id not in self.candidates:
            raise MemoryCandidateNotFoundError(
                f"Memory candidate not found: {candidate_id}"
            )

        return self.candidates[candidate_id]

    def approve(
        self,
        candidate_id: str,
        reason: str = "",
        reviewed_at: str = "",
    ) -> MemoryCandidate:
        """Approve a candidate without creating durable memory."""

        candidate = self.get(candidate_id)
        candidate.approve(reason=reason, reviewed_at=reviewed_at)
        return candidate

    def reject(
        self,
        candidate_id: str,
        reason: str = "",
        reviewed_at: str = "",
    ) -> MemoryCandidate:
        """Reject a candidate without creating durable memory."""

        candidate = self.get(candidate_id)
        candidate.reject(reason=reason, reviewed_at=reviewed_at)
        return candidate

    def clear(self) -> None:
        """Clear the in-memory review queue."""

        self.candidates.clear()

    def _find_duplicate(
        self,
        candidate: MemoryCandidate,
    ) -> MemoryCandidate | None:
        for existing in self.candidates.values():
            if existing.id == candidate.id:
                return existing
            if (
                existing.candidate_type == candidate.candidate_type
                and existing.content.lower() == candidate.content.lower()
            ):
                return existing

        return None
