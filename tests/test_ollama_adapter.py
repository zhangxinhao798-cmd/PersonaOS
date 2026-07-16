"""Tests for OllamaAdapter provider transport boundary."""

import json

import pytest

from backend.adapters import (
    OllamaAdapter,
    OllamaResponseError,
    OllamaTransportError,
)
from backend.models import LLMResponse, ProviderConfig, RuntimeContext


class FakeHttpClient:
    def __init__(
        self,
        response: dict | bytes | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response or {"response": "hello from ollama"}
        self.error = error
        self.calls: list[dict] = []

    def __call__(
        self,
        endpoint: str,
        payload: dict,
        headers: dict,
        timeout: float,
    ) -> bytes:
        self.calls.append(
            {
                "endpoint": endpoint,
                "payload": payload,
                "headers": headers,
                "timeout": timeout,
            }
        )

        if self.error is not None:
            raise self.error

        if isinstance(self.response, bytes):
            return self.response

        return json.dumps(self.response).encode("utf-8")


def ollama_config(
    model: str = "test-model",
    endpoint: str = "http://example.test",
    **kwargs,
) -> ProviderConfig:
    return ProviderConfig(
        provider="ollama",
        model=model,
        endpoint=endpoint,
        **kwargs,
    )


def test_adapter_initializes_with_provider_config() -> None:
    config = ollama_config(
        api_key="secret",
        options={"temperature": 0.2},
    )

    adapter = OllamaAdapter(config=config, http_client=FakeHttpClient())

    assert adapter.config.provider == "ollama"
    assert adapter.config.model == "test-model"
    assert adapter.config.endpoint == "http://example.test"
    assert adapter.config.api_key == "secret"
    assert adapter.config.options == {"temperature": 0.2}


def test_adapter_does_not_own_model_or_endpoint_defaults() -> None:
    adapter = OllamaAdapter(
        config=ProviderConfig(provider="ollama"),
        http_client=FakeHttpClient(),
    )

    assert adapter.config.provider == "ollama"
    assert adapter.config.model == ""
    assert adapter.config.endpoint == ""


def test_correct_endpoint_is_constructed() -> None:
    fake_client = FakeHttpClient()
    adapter = OllamaAdapter(
        config=ollama_config(endpoint="http://localhost:11434/"),
        http_client=fake_client,
    )

    adapter.generate(RuntimeContext(), "hello")

    assert fake_client.calls[0]["endpoint"] == (
        "http://localhost:11434/api/generate"
    )


def test_correct_model_and_rendered_prompt_are_sent() -> None:
    fake_client = FakeHttpClient()
    adapter = OllamaAdapter(
        config=ollama_config(model="custom-model"),
        http_client=fake_client,
    )
    runtime_context = RuntimeContext(
        active_persona={"name": "Architect"},
        memories=["memory"],
    )

    adapter.generate(runtime_context, "current input")

    payload = fake_client.calls[0]["payload"]
    assert payload["model"] == "custom-model"
    assert "## Persona" in payload["prompt"]
    assert "Architect" in payload["prompt"]
    assert "## Memory" in payload["prompt"]
    assert "memory" in payload["prompt"]
    assert "## User Input\ncurrent input" in payload["prompt"]


def test_stream_is_false() -> None:
    fake_client = FakeHttpClient()
    adapter = OllamaAdapter(config=ollama_config(), http_client=fake_client)

    adapter.generate(RuntimeContext(), "hello")

    assert fake_client.calls[0]["payload"]["stream"] is False


def test_configured_options_are_preserved() -> None:
    fake_client = FakeHttpClient()
    adapter = OllamaAdapter(
        config=ollama_config(options={"temperature": 0.1, "num_predict": 64}),
        http_client=fake_client,
    )

    adapter.generate(RuntimeContext(), "hello")

    assert fake_client.calls[0]["payload"]["options"] == {
        "temperature": 0.1,
        "num_predict": 64,
    }


def test_successful_response_becomes_llm_response() -> None:
    fake_client = FakeHttpClient(response={"response": "generated answer"})
    adapter = OllamaAdapter(
        config=ollama_config(model="qwen3:14b"),
        http_client=fake_client,
    )

    response = adapter.generate(RuntimeContext(), "hello")

    assert isinstance(response, LLMResponse)
    assert response.content == "generated answer"
    assert response.provider == "ollama"
    assert response.model == "qwen3:14b"


def test_usage_metadata_is_mapped() -> None:
    fake_client = FakeHttpClient(
        response={
            "response": "generated answer",
            "total_duration": 10,
            "load_duration": 2,
            "prompt_eval_count": 3,
            "prompt_eval_duration": 4,
            "eval_count": 5,
            "eval_duration": 6,
            "done_reason": "stop",
            "ignored": "not usage",
        }
    )
    adapter = OllamaAdapter(config=ollama_config(), http_client=fake_client)

    response = adapter.generate(RuntimeContext(), "hello")

    assert response.usage == {
        "total_duration": 10,
        "load_duration": 2,
        "prompt_eval_count": 3,
        "prompt_eval_duration": 4,
        "eval_count": 5,
        "eval_duration": 6,
        "done_reason": "stop",
    }


def test_empty_response_content_is_handled() -> None:
    fake_client = FakeHttpClient(response={"response": ""})
    adapter = OllamaAdapter(config=ollama_config(), http_client=fake_client)

    with pytest.raises(OllamaResponseError):
        adapter.generate(RuntimeContext(), "hello")


def test_missing_response_content_is_handled() -> None:
    fake_client = FakeHttpClient(response={"done": True})
    adapter = OllamaAdapter(config=ollama_config(), http_client=fake_client)

    with pytest.raises(OllamaResponseError):
        adapter.generate(RuntimeContext(), "hello")


def test_invalid_json_is_handled() -> None:
    fake_client = FakeHttpClient(response=b"{invalid json")
    adapter = OllamaAdapter(config=ollama_config(), http_client=fake_client)

    with pytest.raises(OllamaResponseError):
        adapter.generate(RuntimeContext(), "hello")


def test_connection_failure_is_normalized() -> None:
    fake_client = FakeHttpClient(error=OSError("connection refused"))
    adapter = OllamaAdapter(config=ollama_config(), http_client=fake_client)

    with pytest.raises(OllamaTransportError):
        adapter.generate(RuntimeContext(), "hello")


def test_runtime_context_and_source_records_remain_unchanged() -> None:
    memory = {"content": "remembered context"}
    knowledge = {"records": ["source-backed fact"]}
    metadata = {"trace_id": "runtime-1"}
    runtime_context = RuntimeContext(
        active_persona={"name": "Architect"},
        memories=[memory],
        knowledge=knowledge,
        metadata=metadata,
    )
    original_state = {
        "active_persona": dict(runtime_context.active_persona),
        "memories": [dict(memory)],
        "knowledge": dict(knowledge),
        "metadata": dict(metadata),
    }
    adapter = OllamaAdapter(config=ollama_config(), http_client=FakeHttpClient())

    adapter.generate(runtime_context, "hello")

    assert runtime_context.active_persona == original_state["active_persona"]
    assert runtime_context.memories == original_state["memories"]
    assert runtime_context.knowledge == original_state["knowledge"]
    assert runtime_context.metadata == original_state["metadata"]
