"""Manual local Ollama smoke test for PersonaOS runtime intelligence.

This script exercises the real local runtime path:

RuntimeContext -> PromptBuilder -> PromptRenderer -> OllamaAdapter
-> local Ollama -> qwen3:14b -> LLMResponse

It does not write durable PersonaOS state.
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.adapters import (  # noqa: E402
    OllamaAdapterError,
    OllamaResponseError,
    OllamaTransportError,
)
from backend.models import RuntimeContext  # noqa: E402
from config.runtime import (  # noqa: E402
    RuntimeConfigError,
    build_adapter_registry,
    load_provider_config,
    resolve_configured_adapter,
)


def build_runtime_context() -> RuntimeContext:
    """Create a minimal runtime context without durable state writes."""

    return RuntimeContext(
        active_persona={
            "name": "PersonaOS Local Smoke Tester",
            "style": "clear, concise, and careful",
        },
        memories=[
            {
                "content": "The user is validating the local PersonaOS runtime path.",
                "category": "working",
                "source": "manual-smoke-test",
            }
        ],
        metadata={
            "script": "scripts/smoke_ollama.py",
            "purpose": "manual local Ollama runtime smoke test",
        },
    )


def main() -> int:
    try:
        config = load_provider_config()
        registry = build_adapter_registry(config, timeout=120.0)
        adapter = resolve_configured_adapter(config, registry)
    except RuntimeConfigError as exc:
        print(f"Runtime configuration failed: {exc}")
        return 1

    runtime_context = build_runtime_context()
    user_input = "请用一句中文确认 PersonaOS 本地运行路径已经连通。"

    try:
        response = adapter.generate(runtime_context, user_input)
    except OllamaTransportError:
        print(
            "Ollama is unavailable or returned a non-success response. "
            "Please confirm Ollama is running at "
            f"{config.endpoint} and that model {config.model} is available."
        )
        return 1
    except OllamaResponseError:
        print(
            "Ollama responded, but PersonaOS could not read generated "
            f"content from model {config.model}. Please confirm the "
            "configured model can be reached."
        )
        return 1
    except OllamaAdapterError:
        print(
            "The Ollama adapter reported an unexpected normalized error. "
            "No durable PersonaOS state was modified."
        )
        return 1

    print(f"provider: {response.provider}")
    print(f"model: {response.model}")
    print("response:")
    print(response.content)

    if response.usage:
        print("usage:")
        for key, value in response.usage.items():
            print(f"  {key}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
