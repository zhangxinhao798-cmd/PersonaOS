"""Run PersonaOS as a minimal local HTTP service."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api import ApiTransport, PersonaRuntimeBundle  # noqa: E402
from backend.api.http_server import create_http_server  # noqa: E402
from backend.core import (  # noqa: E402
    PersonaLibraryEngine,
    PersonaPackageLoader,
    PersonaSelector,
)
from backend.engine.runtime_context_assembler import (  # noqa: E402
    RuntimeContextAssembler,
)
from backend.runtime import ChatApiBoundary, ChatRuntime  # noqa: E402
from scripts.chat_persona import (  # noqa: E402
    DEFAULT_PERSONAS_DIR,
    build_persona_os_context,
    configured_adapter,
    default_persona_package_id,
    discover_persona_packages,
    prepare_persona_for_cli_runtime,
    provider_config,
)


class LocalPersonaRuntimeProvider:
    """Build runtime-ready persona dependencies for API sessions."""

    def __init__(
        self,
        personas_dir: Path = DEFAULT_PERSONAS_DIR,
        default_persona_id: str | None = None,
    ) -> None:
        self.personas_dir = personas_dir
        self.default_persona_id = default_persona_id or default_persona_package_id()

    def list_personas(self) -> list[dict]:
        """Return API-safe summaries for valid local persona packages."""

        summaries = []
        loader = PersonaPackageLoader()
        for entry in discover_persona_packages(self.personas_dir):
            package = loader.load(self.personas_dir / entry.id)
            profile = entry.profile
            summaries.append(
                {
                    "id": entry.id,
                    "name": entry.name,
                    "current_version_id": entry.current_version_id,
                    "description": entry.description,
                    "traits": dict(profile.traits) if profile else {},
                    "style": profile.style if profile else "",
                    "suitable_scenarios": list(
                        package.manifest.metadata.get("suitable_scenarios", [])
                    ),
                }
            )
        return summaries

    def get_runtime_bundle(
        self,
        persona_id: str | None = None,
    ) -> PersonaRuntimeBundle:
        """Build one runtime dependency bundle without durable writes."""

        resolved_persona_id = persona_id or self.default_persona_id
        entry = prepare_persona_for_cli_runtime(
            self.personas_dir / resolved_persona_id
        )
        library = PersonaLibraryEngine()
        library.add_persona(entry)
        chat_runtime = ChatRuntime(
            persona_selector=PersonaSelector(library),
            adapter=configured_adapter(provider_config()),
            runtime_context_assembler=RuntimeContextAssembler(),
        )
        return PersonaRuntimeBundle(
            persona_id=entry.id,
            name=entry.name,
            persona_entry=entry,
            persona_os_context=build_persona_os_context(entry),
            chat_runtime=chat_runtime,
            metadata={"transport": "http"},
        )


def build_api_transport(
    personas_dir: Path = DEFAULT_PERSONAS_DIR,
    default_persona_id: str | None = None,
) -> ApiTransport:
    """Build the API transport using existing runtime boundaries."""

    runtime_provider = LocalPersonaRuntimeProvider(
        personas_dir=personas_dir,
        default_persona_id=default_persona_id,
    )
    return ApiTransport(
        chat_api=ChatApiBoundary(),
        runtime_provider=runtime_provider,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the local PersonaOS HTTP API service."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--persona",
        metavar="PACKAGE_ID",
        help="Default persona package id for sessions without persona_id.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    api_transport = build_api_transport(default_persona_id=args.persona)
    server = create_http_server(
        api_transport,
        host=args.host,
        port=args.port,
    )
    print("PersonaOS HTTP API")
    print(f"Listening on http://{args.host}:{args.port}")
    print("Available endpoints:")
    print("  GET    /personas")
    print("  POST   /sessions")
    print("  GET    /sessions/{id}")
    print("  DELETE /sessions/{id}")
    print("  POST   /sessions/{id}/messages")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("PersonaOS HTTP API stopped.")
        return 0
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
