"""Tests for Memory Promotion Boundary v1."""

import copy
import inspect

import pytest

from backend.core.memory import MemoryEngine
from backend.core.memory_candidate import CandidateExtractor, ReviewQueue
from backend.core.memory_promotion import (
    CandidateNotApprovedError,
    InvalidMemoryCandidateError,
    MemoryPromotionBoundary,
)
from backend.core import memory_candidate as memory_candidate_module
from backend.runtime import session as runtime_session_module
from tests.test_runtime_session import make_entry


def approved_candidate():
    candidate = CandidateExtractor().extract(
        {
            "role": "user",
            "content": "I prefer local-first memory systems.",
            "created_at": "2026-07-16T00:00:00Z",
            "metadata": {"session_id": "session-1"},
        }
    )[0]
    ReviewQueue().add(candidate)
    candidate.approve(
        reason="Human approved.",
        reviewed_at="2026-07-16T00:01:00Z",
    )
    return candidate


def test_approved_candidate_can_be_promoted() -> None:
    candidate = approved_candidate()
    memory_engine = MemoryEngine()

    memory = MemoryPromotionBoundary(memory_engine).promote(candidate)

    assert memory in memory_engine.get_memories()
    assert memory.content == candidate.content
    assert memory.category == candidate.category
    assert memory.confidence == candidate.confidence
    assert memory.importance == candidate.importance
    assert memory.source == f"memory_candidate:{candidate.id}"
    assert memory.timestamp == candidate.reviewed_at


def test_pending_candidate_cannot_be_promoted() -> None:
    candidate = CandidateExtractor().extract(
        {"role": "user", "content": "I like explicit review."}
    )[0]

    with pytest.raises(CandidateNotApprovedError):
        MemoryPromotionBoundary(MemoryEngine()).promote(candidate)


def test_rejected_candidate_cannot_be_promoted() -> None:
    candidate = CandidateExtractor().extract(
        {"role": "user", "content": "I like reversible memory."}
    )[0]
    candidate.reject(reason="Not stable enough.")

    with pytest.raises(CandidateNotApprovedError):
        MemoryPromotionBoundary(MemoryEngine()).promote(candidate)


def test_promotion_preserves_candidate_data_integrity() -> None:
    candidate = approved_candidate()
    before = copy.deepcopy(candidate.to_dict())

    memory = MemoryPromotionBoundary(MemoryEngine()).promote(candidate)

    assert memory.content == before["content"]
    assert memory.category == before["category"]
    assert memory.confidence == before["confidence"]
    assert memory.importance == before["importance"]
    assert candidate.to_dict() == before


def test_promotion_preserves_provenance_in_memory_source() -> None:
    candidate = approved_candidate()

    memory = MemoryPromotionBoundary(MemoryEngine()).promote(candidate)

    assert candidate.id in memory.source
    assert memory.source.startswith("memory_candidate:")


def test_invalid_candidate_content_is_rejected() -> None:
    candidate = approved_candidate()
    candidate.content = "   "

    with pytest.raises(InvalidMemoryCandidateError):
        MemoryPromotionBoundary(MemoryEngine()).promote(candidate)


def test_invalid_candidate_confidence_is_rejected() -> None:
    candidate = approved_candidate()
    candidate.confidence = 1.5

    with pytest.raises(InvalidMemoryCandidateError):
        MemoryPromotionBoundary(MemoryEngine()).promote(candidate)


def test_invalid_candidate_importance_is_rejected() -> None:
    candidate = approved_candidate()
    candidate.importance = -0.1

    with pytest.raises(InvalidMemoryCandidateError):
        MemoryPromotionBoundary(MemoryEngine()).promote(candidate)


def test_promotion_does_not_modify_persona_identity() -> None:
    entry = make_entry()
    before_profile = copy.deepcopy(entry.profile.__dict__)
    before_version = copy.deepcopy(entry.versions[0].__dict__)

    MemoryPromotionBoundary(MemoryEngine()).promote(approved_candidate())

    assert entry.profile.__dict__ == before_profile
    assert entry.versions[0].__dict__ == before_version


def test_runtime_and_candidate_pipeline_do_not_write_memory_engine() -> None:
    runtime_source = inspect.getsource(runtime_session_module)
    candidate_source = inspect.getsource(memory_candidate_module)

    assert "MemoryEngine" not in runtime_source
    assert "create_memory(" not in runtime_source
    assert "from backend.core.memory" not in candidate_source
    assert "create_memory(" not in candidate_source


def test_promotion_boundary_is_the_memory_engine_connection() -> None:
    boundary_source = inspect.getsource(MemoryPromotionBoundary)

    assert "create_memory(" in boundary_source
    assert "MemoryEngine" in boundary_source
