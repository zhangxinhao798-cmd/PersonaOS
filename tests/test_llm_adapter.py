"""Tests for provider-independent LLM adapter boundaries."""

import pytest

from backend.adapters import BaseLLMAdapter
from backend.models import LLMResponse, RuntimeContext


class EchoLLMAdapter(BaseLLMAdapter):
    """Minimal test adapter that exercises the base adapter contract."""

    def generate(
        self,
        runtime_context: RuntimeContext,
        user_input: str,
    ) -> LLMResponse:
        return LLMResponse(
            content=user_input,
            metadata={"runtime_context": runtime_context},
        )


def test_base_llm_adapter_requires_generate_implementation() -> None:
    with pytest.raises(TypeError):
        BaseLLMAdapter()


def test_base_llm_adapter_accepts_runtime_context_and_user_input() -> None:
    runtime_context = RuntimeContext(
        active_persona={"name": "Runtime Tester"},
        metadata={"query": "adapter boundary"},
    )

    response = EchoLLMAdapter().generate(
        runtime_context,
        "hello runtime",
    )

    assert isinstance(response, LLMResponse)
    assert response.content == "hello runtime"
    assert response.metadata["runtime_context"] is runtime_context


def test_llm_response_initializes_with_standard_fields() -> None:
    response = LLMResponse(
        content="standard response",
        metadata={"confidence": 0.8},
        provider="test-provider",
        model="test-model",
        usage={"input_tokens": 5, "output_tokens": 2},
    )

    assert response.content == "standard response"
    assert response.metadata == {"confidence": 0.8}
    assert response.provider == "test-provider"
    assert response.model == "test-model"
    assert response.usage == {"input_tokens": 5, "output_tokens": 2}


def test_llm_response_defaults_are_independent() -> None:
    first = LLMResponse()
    second = LLMResponse()

    first.metadata["trace_id"] = "response-1"
    first.usage["tokens"] = 7

    assert first.metadata == {"trace_id": "response-1"}
    assert first.usage == {"tokens": 7}
    assert second.metadata == {}
    assert second.usage == {}
