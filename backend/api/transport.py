"""Dependency-free API transport boundary for PersonaOS."""

from dataclasses import dataclass, field
from typing import Protocol

from backend.models.context import PersonaOSContext
from backend.models.llm_response import LLMResponse
from backend.models.persona_library import PersonaLibraryEntry
from backend.runtime import (
    ChatApiBoundary,
    DuplicateSessionError,
    EmptyUserInputError,
    InvalidSessionError,
    ManagedSession,
    SessionManagerError,
    SessionNotFoundError,
)
from backend.runtime.chat_runtime import ChatRuntime
from backend.runtime.memory_runtime import RuntimeMemoryRetriever


class ApiTransportError(Exception):
    """Base API transport error."""


class ApiValidationError(ApiTransportError):
    """Raised when an API request is malformed."""


class PersonaRuntimeProvider(Protocol):
    """Provides runtime-ready persona dependencies for session creation."""

    def list_personas(self) -> list[dict]:
        """Return API-safe persona summaries."""

    def get_runtime_bundle(self, persona_id: str | None = None) -> "PersonaRuntimeBundle":
        """Return runtime dependencies for a selected persona."""


class MemoryReviewProvider(Protocol):
    """Provides controlled review actions for memory candidates."""

    def list_candidates(self, status: str | None = None) -> list[object]:
        """Return queued candidates."""

    def approve_candidate(
        self,
        candidate_id: str,
        reason: str = "",
        reviewed_at: str = "",
    ) -> object:
        """Approve a queued candidate."""

    def reject_candidate(
        self,
        candidate_id: str,
        reason: str = "",
        reviewed_at: str = "",
    ) -> object:
        """Reject a queued candidate."""

    def promote_candidate(self, candidate_id: str) -> object:
        """Promote an approved candidate through the configured boundary."""

    def clear_candidates(self) -> None:
        """Clear queued candidates."""


@dataclass
class PersonaRuntimeBundle:
    """Runtime dependencies needed to create one temporary session."""

    persona_id: str
    name: str
    persona_entry: PersonaLibraryEntry
    persona_os_context: PersonaOSContext
    chat_runtime: ChatRuntime
    memory_retriever: RuntimeMemoryRetriever | None = None
    candidate_extractor: object | None = None
    review_queue: object | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.metadata = dict(self.metadata or {})


@dataclass
class ApiTransportResponse:
    """Framework-independent HTTP-like response boundary."""

    status_code: int
    body: dict = field(default_factory=dict)


class ApiTransport:
    """HTTP/API transport boundary above ChatApiBoundary.

    ApiTransport owns request routing and validation only. It never calls
    providers, adapters, core engines, or prompt/runtime internals directly.
    """

    def __init__(
        self,
        chat_api: ChatApiBoundary,
        runtime_provider: PersonaRuntimeProvider,
        memory_review_api: MemoryReviewProvider | None = None,
    ) -> None:
        self.chat_api = chat_api
        self.runtime_provider = runtime_provider
        self.memory_review_api = memory_review_api

    def handle_request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
    ) -> ApiTransportResponse:
        """Handle one HTTP-like API request."""

        normalized_method = method.upper()
        segments = self._path_segments(path)
        request_body = dict(body or {})

        try:
            if normalized_method == "GET" and segments == ["memory", "candidates"]:
                return self._list_memory_candidates(request_body)

            if normalized_method == "DELETE" and segments == ["memory", "candidates"]:
                return self._clear_memory_candidates()

            if (
                normalized_method == "POST"
                and len(segments) == 4
                and segments[0] == "memory"
                and segments[1] == "candidates"
            ):
                return self._handle_memory_candidate_action(
                    candidate_id=segments[2],
                    action=segments[3],
                    body=request_body,
                )

            if normalized_method == "GET" and segments == ["personas"]:
                return self._list_personas()

            if normalized_method == "POST" and segments == ["sessions"]:
                return self._create_session(request_body)

            if normalized_method == "GET" and segments == ["sessions"]:
                return self._list_sessions()

            if len(segments) == 2 and segments[0] == "sessions":
                session_id = segments[1]
                if normalized_method == "GET":
                    return self._get_session(session_id)
                if normalized_method == "DELETE":
                    return self._delete_session(session_id)

            if (
                normalized_method == "GET"
                and len(segments) == 3
                and segments[0] == "sessions"
                and segments[2] == "history"
            ):
                return self._get_session_history(segments[1])

            if (
                normalized_method == "POST"
                and len(segments) == 3
                and segments[0] == "sessions"
                and segments[2] == "messages"
            ):
                return self._send_message(segments[1], request_body)

            return ApiTransportResponse(
                status_code=404,
                body={"error": "not_found", "message": "Route not found."},
            )
        except ApiValidationError as exc:
            return ApiTransportResponse(
                status_code=400,
                body={"error": "validation_error", "message": str(exc)},
            )
        except EmptyUserInputError as exc:
            return ApiTransportResponse(
                status_code=400,
                body={"error": "empty_user_input", "message": str(exc)},
            )
        except SessionNotFoundError as exc:
            return ApiTransportResponse(
                status_code=404,
                body={"error": "session_not_found", "message": str(exc)},
            )
        except DuplicateSessionError as exc:
            return ApiTransportResponse(
                status_code=409,
                body={"error": "duplicate_session", "message": str(exc)},
            )
        except (InvalidSessionError, SessionManagerError) as exc:
            return ApiTransportResponse(
                status_code=400,
                body={"error": "session_error", "message": str(exc)},
            )
        except Exception:
            return ApiTransportResponse(
                status_code=500,
                body={
                    "error": "api_transport_error",
                    "message": "API transport request failed.",
                },
            )

    def _list_personas(self) -> ApiTransportResponse:
        return ApiTransportResponse(
            status_code=200,
            body={"personas": self.runtime_provider.list_personas()},
        )

    def _create_session(self, body: dict) -> ApiTransportResponse:
        persona_id = body.get("persona_id")
        session_id = body.get("session_id")
        if session_id is not None and not isinstance(session_id, str):
            raise ApiValidationError("session_id must be a string.")
        if persona_id is not None and not isinstance(persona_id, str):
            raise ApiValidationError("persona_id must be a string.")

        bundle = self.runtime_provider.get_runtime_bundle(persona_id)
        managed_session = self.chat_api.create_session(
            persona_entry=bundle.persona_entry,
            persona_os_context=bundle.persona_os_context,
            chat_runtime=bundle.chat_runtime,
            session_id=session_id,
            metadata={
                "persona_id": bundle.persona_id,
                "persona_name": bundle.name,
                **bundle.metadata,
            },
            memory_retriever=bundle.memory_retriever,
            candidate_extractor=bundle.candidate_extractor,
            review_queue=bundle.review_queue,
        )
        return ApiTransportResponse(
            status_code=201,
            body={"session": self._serialize_session(managed_session)},
        )

    def _list_sessions(self) -> ApiTransportResponse:
        sessions = self.chat_api.list_sessions()
        return ApiTransportResponse(
            status_code=200,
            body={
                "sessions": [
                    self._serialize_session(session)
                    for session in sessions
                ]
            },
        )

    def _get_session(self, session_id: str) -> ApiTransportResponse:
        managed_session = self.chat_api.get_session(session_id)
        return ApiTransportResponse(
            status_code=200,
            body={"session": self._serialize_session(managed_session)},
        )

    def _get_session_history(self, session_id: str) -> ApiTransportResponse:
        history = self.chat_api.get_history(session_id)
        return ApiTransportResponse(
            status_code=200,
            body={"session_id": session_id, "history": history},
        )

    def _delete_session(self, session_id: str) -> ApiTransportResponse:
        self.chat_api.delete_session(session_id)
        return ApiTransportResponse(
            status_code=200,
            body={"deleted": True, "session_id": session_id},
        )

    def _send_message(self, session_id: str, body: dict) -> ApiTransportResponse:
        user_input = body.get("message", body.get("user_input"))
        if not isinstance(user_input, str) or not user_input.strip():
            raise ApiValidationError("message is required.")

        managed_session = self.chat_api.get_session(session_id)
        response = self.chat_api.send_message(session_id, user_input)
        return ApiTransportResponse(
            status_code=200,
            body=self._serialize_message_response(managed_session, response),
        )

    def _list_memory_candidates(self, body: dict) -> ApiTransportResponse:
        review_api = self._require_memory_review_api()
        status = body.get("status")
        if status is not None and not isinstance(status, str):
            raise ApiValidationError("status must be a string.")

        try:
            candidates = review_api.list_candidates(status=status)
        except Exception as exc:
            return self._memory_review_error_response(exc)

        return ApiTransportResponse(
            status_code=200,
            body={
                "candidates": [
                    self._serialize_memory_candidate(candidate)
                    for candidate in candidates
                ]
            },
        )

    def _clear_memory_candidates(self) -> ApiTransportResponse:
        review_api = self._require_memory_review_api()
        try:
            review_api.clear_candidates()
        except Exception as exc:
            return self._memory_review_error_response(exc)

        return ApiTransportResponse(
            status_code=200,
            body={"cleared": True},
        )

    def _handle_memory_candidate_action(
        self,
        candidate_id: str,
        action: str,
        body: dict,
    ) -> ApiTransportResponse:
        if not candidate_id.strip():
            raise ApiValidationError("candidate_id is required.")

        review_api = self._require_memory_review_api()
        reason = body.get("reason", "")
        reviewed_at = body.get("reviewed_at", "")
        if not isinstance(reason, str):
            raise ApiValidationError("reason must be a string.")
        if not isinstance(reviewed_at, str):
            raise ApiValidationError("reviewed_at must be a string.")

        try:
            if action == "approve":
                candidate = review_api.approve_candidate(
                    candidate_id,
                    reason=reason,
                    reviewed_at=reviewed_at,
                )
                return ApiTransportResponse(
                    status_code=200,
                    body={
                        "candidate": self._serialize_memory_candidate(candidate)
                    },
                )

            if action == "reject":
                candidate = review_api.reject_candidate(
                    candidate_id,
                    reason=reason,
                    reviewed_at=reviewed_at,
                )
                return ApiTransportResponse(
                    status_code=200,
                    body={
                        "candidate": self._serialize_memory_candidate(candidate)
                    },
                )

            if action == "promote":
                memory = review_api.promote_candidate(candidate_id)
                return ApiTransportResponse(
                    status_code=201,
                    body={
                        "candidate_id": candidate_id,
                        "memory": self._serialize_memory_record(memory),
                    },
                )
        except Exception as exc:
            return self._memory_review_error_response(exc)

        return ApiTransportResponse(
            status_code=404,
            body={
                "error": "not_found",
                "message": "Memory candidate action not found.",
            },
        )

    def _require_memory_review_api(self) -> MemoryReviewProvider:
        if self.memory_review_api is None:
            raise ApiValidationError("Memory review controls are not configured.")

        return self.memory_review_api

    def _path_segments(self, path: str) -> list[str]:
        clean_path = path.split("?", 1)[0].strip("/")
        if not clean_path:
            return []
        return [segment for segment in clean_path.split("/") if segment]

    def _serialize_session(self, managed_session: ManagedSession) -> dict:
        persona = managed_session.active_persona_reference
        return {
            "session_id": managed_session.session_id,
            "active_persona": {
                "id": persona.id,
                "name": persona.name,
                "current_version_id": persona.current_version_id,
            },
            "turn_count": managed_session.runtime_session.turn_count(),
            "metadata": dict(managed_session.metadata),
        }

    def _serialize_llm_response(self, response: LLMResponse) -> dict:
        return {
            "content": response.content,
            "provider": response.provider,
            "model": response.model,
            "metadata": dict(response.metadata),
            "usage": dict(response.usage),
        }

    def _serialize_memory_candidate(self, candidate: object) -> dict:
        if hasattr(candidate, "to_dict"):
            return dict(candidate.to_dict())

        return {
            "id": getattr(candidate, "id", ""),
            "source_turn": dict(getattr(candidate, "source_turn", {}) or {}),
            "candidate_type": getattr(candidate, "candidate_type", ""),
            "content": getattr(candidate, "content", ""),
            "confidence": getattr(candidate, "confidence", 0.0),
            "reason": getattr(candidate, "reason", ""),
            "category": getattr(candidate, "category", ""),
            "importance": getattr(candidate, "importance", 0.0),
            "metadata": dict(getattr(candidate, "metadata", {}) or {}),
            "created_at": getattr(candidate, "created_at", ""),
            "review_status": getattr(candidate, "review_status", ""),
            "reviewed_at": getattr(candidate, "reviewed_at", ""),
            "review_reason": getattr(candidate, "review_reason", ""),
        }

    def _serialize_memory_record(self, memory: object) -> dict:
        state = getattr(memory, "state", "")
        return {
            "content": getattr(memory, "content", ""),
            "category": getattr(memory, "category", ""),
            "confidence": getattr(memory, "confidence", 0.0),
            "importance": getattr(memory, "importance", 0.0),
            "source": getattr(memory, "source", ""),
            "timestamp": getattr(memory, "timestamp", ""),
            "state": getattr(state, "value", str(state)),
        }

    def _memory_review_error_response(self, exc: Exception) -> ApiTransportResponse:
        error_name = exc.__class__.__name__
        if error_name == "MemoryCandidateNotFoundError":
            return ApiTransportResponse(
                status_code=404,
                body={"error": "candidate_not_found", "message": str(exc)},
            )
        if error_name == "CandidateNotApprovedError":
            return ApiTransportResponse(
                status_code=400,
                body={"error": "candidate_not_approved", "message": str(exc)},
            )
        if error_name in {
            "InvalidMemoryCandidateError",
            "MemoryPromotionError",
            "MemoryReviewValidationError",
        }:
            return ApiTransportResponse(
                status_code=400,
                body={"error": "memory_review_error", "message": str(exc)},
            )

        return ApiTransportResponse(
            status_code=500,
            body={
                "error": "memory_review_error",
                "message": "Memory review request failed.",
            },
        )

    def _serialize_message_response(
        self,
        managed_session: ManagedSession,
        response: LLMResponse,
    ) -> dict:
        persona = managed_session.active_persona_reference
        return {
            "session_id": managed_session.session_id,
            "persona": {
                "id": persona.id,
                "name": persona.name,
                "version": persona.current_version_id,
            },
            "message": {
                "role": "assistant",
                "content": response.content,
            },
            "model": {
                "provider": response.provider,
                "name": response.model,
            },
            "metadata": dict(response.metadata),
            "usage": dict(response.usage),
        }
