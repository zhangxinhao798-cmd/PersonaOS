"""Provider adapter registry boundary for PersonaOS runtime intelligence."""

from typing import Any


class AdapterRegistry:
    """Deterministic provider adapter discovery boundary.

    The registry stores provider adapter instances by provider name only. It
    does not select models, call adapters, orchestrate runtime flow, or perform
    provider-specific behavior.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, Any] = {}

    def register(self, adapter: Any) -> Any:
        """Register an adapter by its provider name."""

        provider = self._adapter_provider(adapter)
        if provider in self._adapters:
            raise ValueError(f"Adapter already registered: {provider}")

        self._adapters[provider] = adapter
        return adapter

    def unregister(self, provider: str) -> Any:
        """Remove and return the adapter registered for a provider."""

        provider_name = self._normalize_provider(provider)
        if provider_name not in self._adapters:
            raise KeyError(f"Unknown provider: {provider_name}")

        return self._adapters.pop(provider_name)

    def get(self, provider: str) -> Any:
        """Return the adapter registered for a provider."""

        provider_name = self._normalize_provider(provider)
        if provider_name not in self._adapters:
            raise KeyError(f"Unknown provider: {provider_name}")

        return self._adapters[provider_name]

    def list_providers(self) -> list[str]:
        """List registered provider names in deterministic order."""

        return sorted(self._adapters.keys())

    def _adapter_provider(self, adapter: Any) -> str:
        provider = getattr(adapter, "provider", "")
        return self._normalize_provider(provider)

    def _normalize_provider(self, provider: str) -> str:
        if not isinstance(provider, str):
            raise TypeError("Provider name must be a string.")

        normalized = provider.strip().lower()
        if not normalized:
            raise ValueError("Provider name is required.")

        return normalized

