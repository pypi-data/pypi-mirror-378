"""Provider/model definitions for LLM integrations.

Centralizes allowed providers and their supported model ids so that new
integrations can be added without touching the game logic.
"""

from typing import Dict, Mapping, Set

_PROVIDERS_TO_MODELS: Dict[str, Set[str]] = {
    "openai": {
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    },
    "mistral": {
        "mistral-small-latest",
        "mistral-medium-latest",
        "mistral-large-latest",
        "mistral-tiny",
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "open-mixtral-8x22b",
    },
}


def supported_providers() -> Set[str]:
    """Return all known provider identifiers."""

    return set(_PROVIDERS_TO_MODELS)


def supported_models(provider: str) -> Set[str]:
    """Return the models registered for a provider.

    Args:
        provider: Provider identifier (case insensitive).
    """

    normalized = validate_provider(provider)
    return set(_PROVIDERS_TO_MODELS[normalized])


def provider_model_map() -> Mapping[str, Set[str]]:
    """Expose the provider/model configuration as a mapping."""

    return _PROVIDERS_TO_MODELS


def validate_provider(provider: str) -> str:
    """Normalize and validate a provider identifier."""

    normalized = (provider or "").strip().lower()
    if normalized not in _PROVIDERS_TO_MODELS:
        raise ValueError(
            f"Unsupported LLM provider '{provider}'. Supported providers: {sorted(_PROVIDERS_TO_MODELS)}"
        )
    return normalized


def validate_model(provider: str, model: str) -> str:
    """Normalize and validate a model identifier for a provider."""

    normalized_provider = validate_provider(provider)
    normalized_model = (model or "").strip()
    allowed = _PROVIDERS_TO_MODELS[normalized_provider]
    if normalized_model not in allowed:
        raise ValueError(
            f"Unsupported model '{model}' for provider '{normalized_provider}'. Allowed models: {sorted(allowed)}"
        )
    return normalized_model


def register_model(provider: str, model: str) -> None:
    """Register an additional model for a provider at runtime."""

    normalized_provider = validate_provider(provider)
    normalized_model = (model or "").strip()
    if not normalized_model:
        raise ValueError("Model identifier cannot be empty")
    _PROVIDERS_TO_MODELS.setdefault(normalized_provider, set()).add(normalized_model)
