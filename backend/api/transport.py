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


@dataclass
class PersonaRuntimeBundle:
    """Runtime dependencies needed to create one temporary session."""

    persona_id: str
    name: str
    persona_entry: PersonaLibraryEntry
    persona_os_context: PersonaOSContext
    chat_runtime: ChatRuntime
    memory_retriever: RuntimeMemoryRetriever | None = None
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
    ) -> None:
        self.chat_api = chat_api
        self.runtime_provider = runtime_provider

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
            if normalized_method == "GET" and segments == ["personas"]:
                return self._list_personas()

            if normalized_method == "POST" and segments == ["sessions"]:
                return self._create_session(request_body)

            if len(segments) == 2 and segments[0] == "sessions":
                session_id = segments[1]
                if normalized_method == "GET":
                    return self._get_session(session_id)
                if normalized_method == "DELETE":
                    return self._delete_session(session_id)

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
        )
        return ApiTransportResponse(
            status_code=201,
            body={"session": self._serialize_session(managed_session)},
        )

    def _get_session(self, session_id: str) -> ApiTransportResponse:
        managed_session = self.chat_api.get_session(session_id)
        return ApiTransportResponse(
            status_code=200,
            body={"session": self._serialize_session(managed_session)},
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
