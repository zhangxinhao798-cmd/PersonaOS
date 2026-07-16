"""Tests for Memory Candidate Review Controls v1."""

import inspect
import json

from backend.api import ApiTransport
from backend.api import transport as api_transport_module
from backend.core.memory import MemoryEngine
from backend.core.memory_candidate import CandidateExtractor, ReviewQueue
from backend.core.memory_promotion import MemoryPromotionBoundary
from backend.runtime import ChatApiBoundary, MemoryReviewApiBoundary
from backend.runtime import memory_review_api as memory_review_api_module

from tests.test_api_transport import FakeRuntimeProvider


def make_candidate(content: str = "I prefer explicit memory review."):
    return CandidateExtractor().extract(
        {
            "role": "user",
            "content": content,
            "created_at": "2026-07-16T00:00:00Z",
            "metadata": {"session_id": "session-1"},
        }
    )[0]


def make_review_api():
    queue = ReviewQueue()
    memory_engine = MemoryEngine()
    review_api = MemoryReviewApiBoundary(
        review_queue=queue,
        promotion_boundary=MemoryPromotionBoundary(memory_engine),
    )
    return review_api, queue, memory_engine


def make_transport_with_review():
    review_api, queue, memory_engine = make_review_api()
    transport = ApiTransport(
        chat_api=ChatApiBoundary(),
        runtime_provider=FakeRuntimeProvider(),
        memory_review_api=review_api,
    )
    return transport, queue, memory_engine


def test_review_api_lists_candidates_by_status() -> None:
    review_api, queue, _ = make_review_api()
    pending = queue.add(make_candidate())
    rejected = queue.add(make_candidate("I like temporary sessions."))
    queue.reject(rejected.id, reason="Not stable enough.")

    candidates = review_api.list_candidates(status="pending")

    assert candidates == [pending]


def test_review_api_approves_candidate_without_promotion() -> None:
    review_api, queue, memory_engine = make_review_api()
    candidate = queue.add(make_candidate())

    approved = review_api.approve_candidate(
        candidate.id,
        reason="Human approved.",
        reviewed_at="2026-07-16T00:01:00Z",
    )

    assert approved.review_status == "approved"
    assert approved.review_reason == "Human approved."
    assert memory_engine.get_memories() == []


def test_review_api_rejects_candidate_without_promotion() -> None:
    review_api, queue, memory_engine = make_review_api()
    candidate = queue.add(make_candidate())

    rejected = review_api.reject_candidate(
        candidate.id,
        reason="Too vague.",
        reviewed_at="2026-07-16T00:01:00Z",
    )

    assert rejected.review_status == "rejected"
    assert rejected.review_reason == "Too vague."
    assert memory_engine.get_memories() == []


def test_review_api_promotes_approved_candidate() -> None:
    review_api, queue, memory_engine = make_review_api()
    candidate = queue.add(make_candidate())
    review_api.approve_candidate(candidate.id, reviewed_at="2026-07-16T00:01:00Z")

    memory = review_api.promote_candidate(candidate.id)

    assert memory in memory_engine.get_memories()
    assert memory.content == candidate.content
    assert memory.source == f"memory_candidate:{candidate.id}"


def test_api_lists_memory_candidates_as_json() -> None:
    transport, queue, _ = make_transport_with_review()
    candidate = queue.add(make_candidate())

    response = transport.handle_request("GET", "/memory/candidates")

    assert response.status_code == 200
    assert response.body["candidates"][0]["id"] == candidate.id
    assert json.loads(json.dumps(response.body))["candidates"][0]["content"]


def test_api_filters_memory_candidates_by_status() -> None:
    transport, queue, _ = make_transport_with_review()
    approved = queue.add(make_candidate())
    rejected = queue.add(make_candidate("I like controlled review."))
    queue.approve(approved.id)
    queue.reject(rejected.id)

    response = transport.handle_request(
        "GET",
        "/memory/candidates",
        {"status": "approved"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.body["candidates"]] == [approved.id]


def test_api_approves_candidate_without_creating_memory() -> None:
    transport, queue, memory_engine = make_transport_with_review()
    candidate = queue.add(make_candidate())

    response = transport.handle_request(
        "POST",
        f"/memory/candidates/{candidate.id}/approve",
        {"reason": "Looks durable.", "reviewed_at": "2026-07-16T00:01:00Z"},
    )

    assert response.status_code == 200
    assert response.body["candidate"]["review_status"] == "approved"
    assert response.body["candidate"]["review_reason"] == "Looks durable."
    assert memory_engine.get_memories() == []


def test_api_rejects_candidate_without_creating_memory() -> None:
    transport, queue, memory_engine = make_transport_with_review()
    candidate = queue.add(make_candidate())

    response = transport.handle_request(
        "POST",
        f"/memory/candidates/{candidate.id}/reject",
        {"reason": "Too temporary."},
    )

    assert response.status_code == 200
    assert response.body["candidate"]["review_status"] == "rejected"
    assert memory_engine.get_memories() == []


def test_api_promotes_only_after_approval() -> None:
    transport, queue, memory_engine = make_transport_with_review()
    candidate = queue.add(make_candidate())

    pending = transport.handle_request(
        "POST",
        f"/memory/candidates/{candidate.id}/promote",
    )
    transport.handle_request(
        "POST",
        f"/memory/candidates/{candidate.id}/approve",
        {"reviewed_at": "2026-07-16T00:01:00Z"},
    )
    promoted = transport.handle_request(
        "POST",
        f"/memory/candidates/{candidate.id}/promote",
    )

    assert pending.status_code == 400
    assert pending.body["error"] == "candidate_not_approved"
    assert promoted.status_code == 201
    assert promoted.body["memory"]["content"] == candidate.content
    assert promoted.body["memory"]["source"] == f"memory_candidate:{candidate.id}"
    assert len(memory_engine.get_memories()) == 1


def test_api_clear_candidates_clears_queue_only() -> None:
    transport, queue, memory_engine = make_transport_with_review()
    queue.add(make_candidate())

    response = transport.handle_request("DELETE", "/memory/candidates")

    assert response.status_code == 200
    assert response.body == {"cleared": True}
    assert queue.list_candidates() == []
    assert memory_engine.get_memories() == []


def test_api_memory_review_routes_require_boundary() -> None:
    transport = ApiTransport(
        chat_api=ChatApiBoundary(),
        runtime_provider=FakeRuntimeProvider(),
    )

    response = transport.handle_request("GET", "/memory/candidates")

    assert response.status_code == 400
    assert response.body["error"] == "validation_error"


def test_memory_review_controls_preserve_architecture_boundaries() -> None:
    api_source = inspect.getsource(api_transport_module)
    review_source = inspect.getsource(memory_review_api_module)

    assert "MemoryEngine" not in api_source
    assert "backend.core.memory" not in api_source
    assert "create_memory(" not in api_source
    assert "MemoryPromotionBoundary" in review_source
