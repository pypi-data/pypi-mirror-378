"""Tests for the schema module."""

import pytest
from nikitas_agents import schema


def test_supported_providers():
    """Test that supported providers returns expected providers."""
    providers = schema.supported_providers()
    assert "openai" in providers
    assert "mistral" in providers
    assert isinstance(providers, set)


def test_supported_models():
    """Test that supported models returns models for each provider."""
    # Test OpenAI models
    openai_models = schema.supported_models("openai")
    assert "gpt-4o-mini" in openai_models
    assert "gpt-4o" in openai_models
    assert isinstance(openai_models, set)
    
    # Test Mistral models
    mistral_models = schema.supported_models("mistral")
    assert "mistral-small-latest" in mistral_models
    assert isinstance(mistral_models, set)


def test_validate_provider():
    """Test provider validation."""
    # Valid providers
    assert schema.validate_provider("openai") == "openai"
    assert schema.validate_provider("mistral") == "mistral"
    assert schema.validate_provider("OpenAI") == "openai"  # Case insensitive
    assert schema.validate_provider(" MISTRAL ") == "mistral"  # Strips whitespace
    
    # Invalid provider
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        schema.validate_provider("invalid_provider")


def test_validate_model():
    """Test model validation."""
    # Valid models
    assert schema.validate_model("openai", "gpt-4o-mini") == "gpt-4o-mini"
    assert schema.validate_model("mistral", "mistral-small-latest") == "mistral-small-latest"
    
    # Invalid model for provider
    with pytest.raises(ValueError, match="Unsupported model"):
        schema.validate_model("openai", "invalid-model")
    
    # Invalid provider
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        schema.validate_model("invalid_provider", "some-model")


def test_provider_model_map():
    """Test that provider model map returns the correct structure."""
    mapping = schema.provider_model_map()
    assert isinstance(mapping, dict)
    assert "openai" in mapping
    assert "mistral" in mapping
    assert isinstance(mapping["openai"], set)
    assert isinstance(mapping["mistral"], set)


def test_register_model():
    """Test runtime model registration."""
    # Register a new model
    schema.register_model("openai", "test-model-123")
    
    # Verify it's now supported
    models = schema.supported_models("openai")
    assert "test-model-123" in models
    
    # Validate the newly registered model
    assert schema.validate_model("openai", "test-model-123") == "test-model-123"
    
    # Test invalid registration
    with pytest.raises(ValueError, match="Model identifier cannot be empty"):
        schema.register_model("openai", "")
