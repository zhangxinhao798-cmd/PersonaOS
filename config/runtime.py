"""Runtime provider configuration loading for PersonaOS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.adapters import AdapterRegistry, OllamaAdapter
from backend.models import ProviderConfig


DEFAULT_RUNTIME_CONFIG_PATH = Path(__file__).with_name("runtime.json")


class RuntimeConfigError(Exception):
    """Raised when runtime provider configuration is invalid."""


def load_provider_config(path: str | Path | None = None) -> ProviderConfig:
    """Load provider configuration from a JSON file."""

    config_path = Path(path) if path is not None else DEFAULT_RUNTIME_CONFIG_PATH
    try:
        raw_config = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeConfigError(
            f"Runtime configuration file not found: {config_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeConfigError("Runtime configuration is not valid JSON.") from exc

    if not isinstance(raw_config, dict):
        raise RuntimeConfigError("Runtime configuration must be a JSON object.")

    return provider_config_from_mapping(raw_config)


def provider_config_from_mapping(raw_config: dict[str, Any]) -> ProviderConfig:
    """Convert a mapping into a validated ProviderConfig."""

    provider = _required_string(raw_config, "provider")
    model = _required_string(raw_config, "model")
    endpoint = _required_string(raw_config, "endpoint")
    api_key = raw_config.get("api_key")
    options = raw_config.get("options", {})

    if api_key is not None and not isinstance(api_key, str):
        raise RuntimeConfigError("Runtime configuration api_key must be a string.")
    if not isinstance(options, dict):
        raise RuntimeConfigError("Runtime configuration options must be an object.")

    return ProviderConfig(
        provider=provider,
        model=model,
        endpoint=endpoint,
        api_key=api_key,
        options=dict(options),
    )


def build_adapter_registry(
    provider_config: ProviderConfig,
    timeout: float = 30.0,
) -> AdapterRegistry:
    """Build an adapter registry for the configured provider."""

    registry = AdapterRegistry()
    provider = _normalize_provider(provider_config.provider)

    if provider == "ollama":
        registry.register(OllamaAdapter(config=provider_config, timeout=timeout))
        return registry

    raise RuntimeConfigError(f"Unsupported runtime provider: {provider}")


def resolve_configured_adapter(
    provider_config: ProviderConfig,
    registry: AdapterRegistry,
) -> Any:
    """Resolve the configured adapter through AdapterRegistry."""

    return registry.get(provider_config.provider)


def _required_string(raw_config: dict[str, Any], key: str) -> str:
    value = raw_config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeConfigError(f"Runtime configuration {key} is required.")

    return value.strip()


def _normalize_provider(provider: str) -> str:
    if not isinstance(provider, str) or not provider.strip():
        raise RuntimeConfigError("Runtime configuration provider is required.")

    return provider.strip().lower()
