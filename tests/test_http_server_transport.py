"""Tests for standard-library HTTP server transport."""

import json
from threading import Thread
from urllib import error, request

from backend.api import ApiTransport
from backend.api.http_server import create_http_server
from backend.runtime import ChatApiBoundary

from tests.test_api_transport import FakeRuntimeProvider


def start_test_server() -> tuple:
    provider = FakeRuntimeProvider()
    transport = ApiTransport(
        chat_api=ChatApiBoundary(),
        runtime_provider=provider,
    )
    server = create_http_server(transport, host="127.0.0.1", port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, provider


def http_json(
    base_url: str,
    method: str,
    path: str,
    body: dict | None = None,
) -> tuple[int, dict]:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    http_request = request.Request(
        f"{base_url}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with request.urlopen(http_request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload
    except error.HTTPError as exc:
        payload = json.loads(exc.read().decode("utf-8"))
        return exc.code, payload


def http_response(
    base_url: str,
    method: str,
    path: str,
    body: dict | None = None,
):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    http_request = request.Request(
        f"{base_url}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    return request.urlopen(http_request, timeout=5)


def test_http_server_starts_and_returns_personas() -> None:
    server, thread, provider = start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        status, payload = http_json(base_url, "GET", "/personas")
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert status == 200
    assert payload["personas"] == provider.list_personas()


def test_http_server_create_session_and_send_message_flow() -> None:
    server, thread, provider = start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        create_status, create_payload = http_json(
            base_url,
            "POST",
            "/sessions",
            {"session_id": "session-1"},
        )
        message_status, message_payload = http_json(
            base_url,
            "POST",
            "/sessions/session-1/messages",
            {"message": "hello over http"},
        )
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert create_status == 201
    assert create_payload["session"]["session_id"] == "session-1"
    assert message_status == 200
    assert message_payload["message"]["content"] == "api transport reply"
    assert message_payload["message"]["role"] == "assistant"
    assert provider.runtime.calls[0]["user_input"] == "hello over http"


def test_http_server_returns_error_response() -> None:
    server, thread, _ = start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        status, payload = http_json(
            base_url,
            "POST",
            "/sessions",
            {"session_id": "session-1"},
        )
        missing_status, missing_payload = http_json(
            base_url,
            "GET",
            "/sessions/missing",
        )
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert status == 201
    assert missing_status == 404
    assert missing_payload["error"] == "session_not_found"


def test_http_server_returns_cors_headers_for_browser_console() -> None:
    server, thread, _ = start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with http_response(base_url, "GET", "/personas") as response:
            allow_origin = response.headers["Access-Control-Allow-Origin"]
            allow_methods = response.headers["Access-Control-Allow-Methods"]
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert allow_origin == "*"
    assert "POST" in allow_methods


def test_http_server_handles_options_preflight() -> None:
    server, thread, _ = start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with http_response(base_url, "OPTIONS", "/sessions") as response:
            status = response.status
            allow_headers = response.headers["Access-Control-Allow-Headers"]
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert status == 204
    assert "Content-Type" in allow_headers
