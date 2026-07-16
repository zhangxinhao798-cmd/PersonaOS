"""Tests for PersonaOS runtime configuration loading."""

import json
from pathlib import Path

import pytest

from backend.adapters import OllamaAdapter
from backend.models import ProviderConfig
from config.runtime import (
    RuntimeConfigError,
    build_adapter_registry,
    load_default_persona_package_id,
    load_provider_config,
    provider_config_from_mapping,
    resolve_configured_adapter,
)


def write_config(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_loads_provider_config_from_json(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "runtime.json",
        {
            "provider": "ollama",
            "model": "qwen3:14b",
            "endpoint": "http://localhost:11434",
            "api_key": "secret",
            "options": {"temperature": 0.1},
        },
    )

    config = load_provider_config(path)

    assert config == ProviderConfig(
        provider="ollama",
        model="qwen3:14b",
        endpoint="http://localhost:11434",
        api_key="secret",
        options={"temperature": 0.1},
    )


def test_default_runtime_config_loads_current_ollama_settings() -> None:
    config = load_provider_config()

    assert config.provider == "ollama"
    assert config.model == "qwen3:14b"
    assert config.endpoint == "http://localhost:11434"
    assert config.options == {}


def test_loads_default_persona_package_id_from_json(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "runtime.json",
        {
            "provider": "ollama",
            "model": "qwen3:14b",
            "endpoint": "http://localhost:11434",
            "default_persona": "strategist",
        },
    )

    assert load_default_persona_package_id(path) == "strategist"


def test_default_persona_package_id_falls_back_to_architect(
    tmp_path: Path,
) -> None:
    path = write_config(
        tmp_path / "runtime.json",
        {
            "provider": "ollama",
            "model": "qwen3:14b",
            "endpoint": "http://localhost:11434",
        },
    )

    assert load_default_persona_package_id(path) == "architect"


def test_default_persona_package_id_must_be_string(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "runtime.json",
        {
            "provider": "ollama",
            "model": "qwen3:14b",
            "endpoint": "http://localhost:11434",
            "default_persona": ["strategist"],
        },
    )

    with pytest.raises(RuntimeConfigError):
        load_default_persona_package_id(path)


def test_missing_required_provider_config_field_is_rejected() -> None:
    with pytest.raises(RuntimeConfigError):
        provider_config_from_mapping(
            {
                "provider": "ollama",
                "endpoint": "http://localhost:11434",
            }
        )


def test_options_must_be_mapping() -> None:
    with pytest.raises(RuntimeConfigError):
        provider_config_from_mapping(
            {
                "provider": "ollama",
                "model": "qwen3:14b",
                "endpoint": "http://localhost:11434",
                "options": ["bad"],
            }
        )


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(RuntimeConfigError):
        load_provider_config(path)


def test_build_adapter_registry_registers_configured_ollama_adapter() -> None:
    config = ProviderConfig(
        provider="ollama",
        model="configured-model",
        endpoint="http://configured-endpoint",
        options={"num_predict": 64},
    )

    registry = build_adapter_registry(config)
    adapter = resolve_configured_adapter(config, registry)

    assert registry.list_providers() == ["ollama"]
    assert isinstance(adapter, OllamaAdapter)
    assert adapter.config.model == "configured-model"
    assert adapter.config.endpoint == "http://configured-endpoint"
    assert adapter.config.options == {"num_predict": 64}


def test_unknown_runtime_provider_is_rejected() -> None:
    config = ProviderConfig(
        provider="openai",
        model="future-model",
        endpoint="https://example.test",
    )

    with pytest.raises(RuntimeConfigError):
        build_adapter_registry(config)


def test_resolve_configured_adapter_uses_registry_lookup() -> None:
    config = ProviderConfig(
        provider=" OLLAMA ",
        model="qwen3:14b",
        endpoint="http://localhost:11434",
    )

    registry = build_adapter_registry(config)
    adapter = resolve_configured_adapter(config, registry)

    assert adapter is registry.get("ollama")
