"""Tests for the agents module."""

import os
import pytest
from unittest.mock import Mock, patch
from nikitas_agents.agents import BaseAgent


class TestBaseAgent:
    """Test cases for BaseAgent class."""

    def test_agent_initialization(self):
        """Test basic agent initialization."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("nikitas_agents.agents.OpenAI") as mock_openai:
                agent = BaseAgent(
                    name="TestAgent",
                    description="A test agent",
                    provider="openai",
                    model="gpt-4o-mini"
                )
                
                assert agent.name == "TestAgent"
                assert agent.description == "A test agent"
                assert agent.provider == "openai"
                assert agent.model == "gpt-4o-mini"
                mock_openai.assert_called_once_with(api_key="test-key")

    def test_agent_missing_api_key(self):
        """Test that agent raises error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="Missing OPENAI_API_KEY"):
                BaseAgent(
                    name="TestAgent",
                    description="A test agent",
                    provider="openai",
                    model="gpt-4o-mini"
                )

    def test_mistral_initialization(self):
        """Test Mistral agent initialization."""
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test-key"}):
            with patch("nikitas_agents.agents.Mistral") as mock_mistral:
                agent = BaseAgent(
                    name="TestAgent",
                    description="A test agent",
                    provider="mistral",
                    model="mistral-small-latest"
                )
                
                assert agent.provider == "mistral"
                assert agent.model == "mistral-small-latest"
                mock_mistral.assert_called_once_with(api_key="test-key")

    def test_invalid_provider(self):
        """Test that invalid provider raises error."""
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            BaseAgent(
                name="TestAgent",
                description="A test agent",
                provider="invalid_provider",
                model="some-model"
            )

    def test_invalid_model(self):
        """Test that invalid model raises error."""
        with pytest.raises(ValueError, match="Unsupported model"):
            BaseAgent(
                name="TestAgent",
                description="A test agent",
                provider="openai",
                model="invalid-model"
            )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("nikitas_agents.agents.OpenAI")
    def test_invoke_openai_fallback(self, mock_openai_class):
        """Test OpenAI invoke method with fallback to chat completions."""
        # Mock the OpenAI client and response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.with_options.return_value = mock_client
        
        # Mock responses.create to raise an exception (trigger fallback)
        mock_client.responses.create.side_effect = Exception("Responses API not available")
        
        # Mock chat.completions.create for fallback
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_completion
        
        agent = BaseAgent(
            name="TestAgent",
            description="A test agent",
            provider="openai",
            model="gpt-4o-mini"
        )
        
        result = agent.invoke("Test prompt")
        assert result == "Test response"
        
        # Verify fallback was called
        mock_client.chat.completions.create.assert_called_once()

    def test_unsupported_runtime_provider(self):
        """Test runtime error for unsupported provider."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("nikitas_agents.agents.OpenAI"):
                agent = BaseAgent(
                    name="TestAgent",
                    description="A test agent",
                    provider="openai",
                    model="gpt-4o-mini"
                )
                
                # Manually change provider to something unsupported
                agent.provider = "unsupported"
                
                with pytest.raises(RuntimeError, match="Unsupported LLM provider at runtime"):
                    agent.invoke("Test prompt")
