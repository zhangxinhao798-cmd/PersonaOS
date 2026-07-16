"""Tests for provider adapter registry boundaries."""

import pytest

from backend.adapters import AdapterRegistry, BaseLLMAdapter
from backend.models import LLMResponse, ProviderConfig, RuntimeContext


class TestAdapter(BaseLLMAdapter):
    provider = "test-provider"

    def generate(
        self,
        runtime_context: RuntimeContext,
        user_input: str,
    ) -> LLMResponse:
        return LLMResponse(content=user_input)


class AlternateAdapter(BaseLLMAdapter):
    provider = "alternate-provider"

    def generate(
        self,
        runtime_context: RuntimeContext,
        user_input: str,
    ) -> LLMResponse:
        return LLMResponse(content=user_input)


def test_registers_adapter_by_provider_name() -> None:
    registry = AdapterRegistry()
    adapter = TestAdapter()

    registry.register(adapter)

    assert registry.get("test-provider") is adapter


def test_duplicate_registration_is_rejected() -> None:
    registry = AdapterRegistry()
    registry.register(TestAdapter())

    with pytest.raises(ValueError):
        registry.register(TestAdapter())


def test_unknown_provider_lookup_is_rejected() -> None:
    registry = AdapterRegistry()

    with pytest.raises(KeyError):
        registry.get("missing-provider")


def test_unregister_removes_provider_adapter() -> None:
    registry = AdapterRegistry()
    adapter = TestAdapter()
    registry.register(adapter)

    removed = registry.unregister("test-provider")

    assert removed is adapter
    assert registry.list_providers() == []
    with pytest.raises(KeyError):
        registry.get("test-provider")


def test_provider_listing_is_deterministic() -> None:
    registry = AdapterRegistry()

    registry.register(TestAdapter())
    registry.register(AlternateAdapter())

    assert registry.list_providers() == [
        "alternate-provider",
        "test-provider",
    ]


def test_provider_lookup_is_normalized() -> None:
    registry = AdapterRegistry()
    adapter = TestAdapter()

    registry.register(adapter)

    assert registry.get(" Test-Provider ") is adapter


def test_provider_config_initializes_with_values() -> None:
    config = ProviderConfig(
        provider="test-provider",
        model="test-model",
        endpoint="http://localhost",
        api_key="secret",
        options={"temperature": 0.2},
    )

    assert config.provider == "test-provider"
    assert config.model == "test-model"
    assert config.endpoint == "http://localhost"
    assert config.api_key == "secret"
    assert config.options == {"temperature": 0.2}


def test_provider_config_defaults_are_independent() -> None:
    first = ProviderConfig()
    second = ProviderConfig()

    first.options["timeout"] = 30

    assert first.provider == ""
    assert first.model == ""
    assert first.endpoint == ""
    assert first.api_key is None
    assert first.options == {"timeout": 30}
    assert second.options == {}
