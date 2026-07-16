"""Standard-library HTTP wrapper for PersonaOS ApiTransport."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Type

from backend.api.transport import ApiTransport


def create_handler(api_transport: ApiTransport) -> Type[BaseHTTPRequestHandler]:
    """Create a request handler bound to an ApiTransport instance."""

    class PersonaOSHttpHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self._handle("GET")

        def do_POST(self) -> None:
            self._handle("POST")

        def do_DELETE(self) -> None:
            self._handle("DELETE")

        def _handle(self, method: str) -> None:
            body = self._read_json_body()
            response = api_transport.handle_request(method, self.path, body)
            payload = json.dumps(response.body).encode("utf-8")
            self.send_response(response.status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def _read_json_body(self) -> dict:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
            if content_length <= 0:
                return {}

            raw_body = self.rfile.read(content_length)
            if not raw_body:
                return {}

            try:
                decoded = raw_body.decode("utf-8")
                parsed = json.loads(decoded)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return {}

            return parsed if isinstance(parsed, dict) else {}

        def log_message(self, format: str, *args) -> None:
            return

    return PersonaOSHttpHandler


def create_http_server(
    api_transport: ApiTransport,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> ThreadingHTTPServer:
    """Create a standard-library HTTP server for PersonaOS API transport."""

    return ThreadingHTTPServer((host, port), create_handler(api_transport))
