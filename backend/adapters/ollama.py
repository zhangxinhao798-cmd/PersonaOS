"""Ollama provider adapter for PersonaOS runtime intelligence."""

import json
import socket
import urllib.error
import urllib.request
from typing import Callable

from backend.adapters.llm import BaseLLMAdapter
from backend.engine.prompt_builder import PromptBuilder
from backend.engine.prompt_renderer import PromptRenderer
from backend.models.llm_response import LLMResponse
from backend.models.provider_config import ProviderConfig
from backend.models.runtime_context import RuntimeContext


class OllamaAdapterError(Exception):
    """Base error for normalized Ollama adapter failures."""


class OllamaTransportError(OllamaAdapterError):
    """Raised when Ollama transport fails before a valid response is parsed."""


class OllamaResponseError(OllamaAdapterError):
    """Raised when Ollama returns an invalid or unusable response."""


HttpClient = Callable[[str, dict, dict, float], bytes]


class OllamaAdapter(BaseLLMAdapter):
    """Provider-specific transport adapter for Ollama.

    The adapter owns HTTP transport and Ollama response translation only. It
    does not mutate RuntimeContext or any durable PersonaOS state.
    """

    provider = "ollama"

    def __init__(
        self,
        config: ProviderConfig | None = None,
        http_client: HttpClient | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.config = self._with_defaults(config)
        self._http_client = http_client or self._post_json
        self.timeout = timeout
        self.prompt_builder = PromptBuilder()
        self.prompt_renderer = PromptRenderer()

    def generate(
        self,
        runtime_context: RuntimeContext,
        user_input: str,
    ) -> LLMResponse:
        """Generate a standardized response through Ollama."""

        prompt_package = self.prompt_builder.build(runtime_context, user_input)
        final_prompt = self.prompt_renderer.render(prompt_package)
        payload = self._request_payload(final_prompt.text)
        raw_response = self._send_request(payload)
        response_data = self._parse_response(raw_response)
        content = response_data.get("response")

        if not isinstance(content, str) or not content:
            raise OllamaResponseError("Ollama response did not include content.")

        return LLMResponse(
            content=content,
            provider=self.provider,
            model=self.config.model,
            metadata=dict(final_prompt.metadata or {}),
            usage=self._usage(response_data),
        )

    def _with_defaults(self, config: ProviderConfig | None) -> ProviderConfig:
        source = config or ProviderConfig()
        return ProviderConfig(
            provider=source.provider or self.provider,
            model=source.model,
            endpoint=source.endpoint,
            api_key=source.api_key,
            options=dict(source.options or {}),
        )

    def _request_payload(self, prompt: str) -> dict:
        return {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": dict(self.config.options or {}),
        }

    def _send_request(self, payload: dict) -> bytes:
        try:
            return self._http_client(
                self._generate_endpoint(),
                payload,
                self._headers(),
                self.timeout,
            )
        except OllamaAdapterError:
            raise
        except (TimeoutError, socket.timeout, urllib.error.URLError, OSError):
            raise OllamaTransportError("Ollama endpoint is unavailable.")

    def _parse_response(self, raw_response: bytes) -> dict:
        try:
            response = json.loads(raw_response.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise OllamaResponseError("Ollama returned invalid JSON.")

        if not isinstance(response, dict):
            raise OllamaResponseError("Ollama returned an invalid response.")

        return response

    def _usage(self, response_data: dict) -> dict:
        usage_fields = (
            "total_duration",
            "load_duration",
            "prompt_eval_count",
            "prompt_eval_duration",
            "eval_count",
            "eval_duration",
            "done_reason",
        )

        return {
            field: response_data[field]
            for field in usage_fields
            if field in response_data
        }

    def _generate_endpoint(self) -> str:
        return f"{self.config.endpoint.rstrip('/')}/api/generate"

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = "Bearer " + self.config.api_key

        return headers

    def _post_json(
        self,
        endpoint: str,
        payload: dict,
        headers: dict,
        timeout: float,
    ) -> bytes:
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", 200)
                if status < 200 or status >= 300:
                    raise OllamaTransportError(
                        "Ollama endpoint returned a non-success status."
                    )

                return response.read()
        except urllib.error.HTTPError:
            raise OllamaTransportError(
                "Ollama endpoint returned a non-success status."
            )
