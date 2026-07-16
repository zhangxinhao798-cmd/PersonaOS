"""Tests for Memory Review / Candidate Pipeline v1."""

import copy
import inspect

from backend.core.memory import MemoryEngine
from backend.core.memory_candidate import (
    CandidateExtractor,
    MemoryCandidateNotFoundError,
    ReviewQueue,
)
from backend.core import memory_candidate as memory_candidate_module
from backend.models import LLMResponse, MemoryCandidate
from backend.runtime import RuntimeSession, SessionManager

from tests.test_runtime_session import FakeChatRuntime, make_context, make_entry


def make_turn(content: str, role: str = "user") -> dict:
    return {
        "role": role,
        "content": content,
        "created_at": "2026-07-16T00:00:00Z",
        "metadata": {"source": "test"},
    }


def test_extracts_user_preference_candidate() -> None:
    candidates = CandidateExtractor().extract(make_turn("I prefer Porsche cars."))

    assert len(candidates) == 1
    candidate = candidates[0]
    assert isinstance(candidate, MemoryCandidate)
    assert candidate.candidate_type == "user_preference"
    assert candidate.content == "User prefers Porsche cars."
    assert candidate.confidence == 0.8
    assert candidate.review_status == "pending"
    assert candidate.metadata["automatic_persistence"] is False


def test_extracts_supported_candidate_types() -> None:
    extractor = CandidateExtractor()

    goal = extractor.extract(make_turn("I want to build PersonaOS."))[0]
    fact = extractor.extract(make_turn("My name is Bilbo."))[0]
    habit = extractor.extract(make_turn("I usually code at night."))[0]

    assert goal.candidate_type == "long_term_goal"
    assert goal.content == "User wants to build PersonaOS."
    assert fact.candidate_type == "explicit_personal_fact"
    assert fact.content == "User stated Bilbo."
    assert habit.candidate_type == "stable_habit"
    assert habit.content == "User often code at night."


def test_extractor_ignores_assistant_turns_and_empty_content() -> None:
    extractor = CandidateExtractor()

    assert extractor.extract(make_turn("I prefer tea.", role="assistant")) == []
    assert extractor.extract(make_turn("   ")) == []


def test_review_queue_adds_lists_and_clears_candidates() -> None:
    candidate = CandidateExtractor().extract(make_turn("I like quiet tools."))[0]
    queue = ReviewQueue()

    queued = queue.add(candidate)

    assert queued is candidate
    assert queue.list_candidates() == [candidate]
    assert queue.list_candidates("pending") == [candidate]

    queue.clear()

    assert queue.list_candidates() == []


def test_review_queue_approves_without_writing_memory_engine() -> None:
    candidate = CandidateExtractor().extract(make_turn("I love local models."))[0]
    queue = ReviewQueue()
    memory_engine = MemoryEngine()
    queue.add(candidate)

    approved = queue.approve(
        candidate.id,
        reason="Human approved.",
        reviewed_at="2026-07-16T00:01:00Z",
    )

    assert approved.review_status == "approved"
    assert approved.review_reason == "Human approved."
    assert approved.reviewed_at == "2026-07-16T00:01:00Z"
    assert memory_engine.get_memories() == []


def test_review_queue_rejects_without_writing_memory_engine() -> None:
    candidate = CandidateExtractor().extract(make_turn("I enjoy temporary notes."))[0]
    queue = ReviewQueue()
    memory_engine = MemoryEngine()
    queue.add(candidate)

    rejected = queue.reject(candidate.id, reason="Not durable.")

    assert rejected.review_status == "rejected"
    assert rejected.review_reason == "Not durable."
    assert memory_engine.get_memories() == []


def test_review_queue_missing_candidate_raises() -> None:
    queue = ReviewQueue()

    try:
        queue.approve("missing")
    except MemoryCandidateNotFoundError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Expected MemoryCandidateNotFoundError")


def test_review_queue_suppresses_duplicates() -> None:
    candidate = CandidateExtractor().extract(make_turn("I like local tools."))[0]
    duplicate = copy.deepcopy(candidate)
    queue = ReviewQueue()

    first = queue.add(candidate)
    second = queue.add(duplicate)

    assert first is candidate
    assert second is candidate
    assert queue.list_candidates() == [candidate]


def test_runtime_session_produces_candidates_without_durable_memory_write() -> None:
    queue = ReviewQueue()
    runtime = FakeChatRuntime(
        responses=[LLMResponse(content="noted for review", provider="fake")]
    )
    memory_engine = MemoryEngine()
    session = RuntimeSession(
        id="candidate-session",
        persona_entry=make_entry(),
        persona_os_context=make_context(),
        chat_runtime=runtime,
        candidate_extractor=CandidateExtractor(),
        review_queue=queue,
    )

    session.send("I prefer local-first tools.")

    candidates = queue.list_candidates()
    history = session.get_history()
    assert len(candidates) == 1
    assert candidates[0].content == "User prefers local-first tools."
    assert history[0]["metadata"]["memory_candidates"] == [candidates[0].id]
    assert history[0]["metadata"]["memory_candidate_count"] == 1
    assert history[0]["metadata"]["memory_candidate_persistence"] == (
        "review_required"
    )
    assert memory_engine.get_memories() == []


def test_runtime_session_without_candidate_pipeline_preserves_existing_behavior() -> None:
    runtime = FakeChatRuntime()
    session = RuntimeSession(
        id="plain-session",
        persona_entry=make_entry(),
        persona_os_context=make_context(),
        chat_runtime=runtime,
    )

    session.send("I prefer local-first tools.")

    assert "memory_candidates" not in session.get_history()[0]["metadata"]


def test_session_manager_passes_candidate_pipeline_to_runtime_session() -> None:
    queue = ReviewQueue()
    manager = SessionManager()
    manager.create_session(
        persona_entry=make_entry(),
        persona_os_context=make_context(),
        chat_runtime=FakeChatRuntime(),
        session_id="session-1",
        candidate_extractor=CandidateExtractor(),
        review_queue=queue,
    )

    manager.send_message("session-1", "I like carefully reviewed memory.")

    assert len(queue.list_candidates()) == 1
    assert queue.list_candidates()[0].review_status == "pending"


def test_candidate_pipeline_does_not_import_or_call_memory_engine() -> None:
    source = inspect.getsource(memory_candidate_module)

    assert "from backend.core.memory" not in source
    assert "MemoryEngine(" not in source
    assert "create_memory(" not in source
    assert "save(" not in source
