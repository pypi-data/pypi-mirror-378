# nikitas-agents

Provider-agnostic wrappers around OpenAI and Mistral SDKs to power LLM-based agents in games or simulations.

## Installation

This package is currently distributed straight from GitHub:

```bash
pip install git+https://github.com/NikitaDmitrieff/nikitas-agents.git
```

## Quick Start

```python
from nikitas_agents.agents import BaseAgent

agent = BaseAgent(
    name="Strategist",
    description="Keeps track of board state",
    provider="openai",
    model="gpt-4o-mini",
)

reply = agent.invoke("Give me one word hint.")
print(reply)
```

Set `OPENAI_API_KEY` or `MISTRAL_API_KEY` in your environment before invoking agents.

## Features

- **Multi-provider support**: Works with both OpenAI and Mistral APIs
- **Model validation**: Ensures you're using supported models for each provider
- **Environment-based configuration**: Automatically loads API keys from environment variables
- **Flexible prompting**: Support for both system and user prompts with customizable parameters

## Supported Providers and Models

### OpenAI
- gpt-4o-mini
- gpt-4o
- gpt-4-turbo
- gpt-4
- gpt-3.5-turbo

### Mistral
- mistral-small-latest
- mistral-medium-latest
- mistral-large-latest
- mistral-tiny
- open-mistral-7b
- open-mixtral-8x7b
- open-mixtral-8x22b

## Usage

### Basic Agent Creation

```python
from nikitas_agents import BaseAgent

# Create an OpenAI agent
openai_agent = BaseAgent(
    name="Assistant",
    description="A helpful assistant",
    provider="openai",
    model="gpt-4o-mini"
)

# Create a Mistral agent
mistral_agent = BaseAgent(
    name="Strategist", 
    description="A strategic thinking agent",
    provider="mistral",
    model="mistral-small-latest"
)
```

### Advanced Usage

```python
response = agent.invoke(
    user_prompt="What's the best strategy for this situation?",
    system_prompt="You are an expert game strategist",
    temperature=0.7,
    max_output_tokens=512,
    timeout=30.0
)
```

### Provider and Model Validation

```python
from nikitas_agents import schema

# Check supported providers
providers = schema.supported_providers()
print(providers)  # {'openai', 'mistral'}

# Check supported models for a provider
models = schema.supported_models('openai')
print(models)  # {'gpt-4o-mini', 'gpt-4o', ...}

# Validate a provider/model combination
validated_model = schema.validate_model('openai', 'gpt-4o-mini')
```

## Environment Setup

Create a `.env` file in your project root:

```
OPENAI_API_KEY=your_openai_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
```

Or set environment variables directly:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export MISTRAL_API_KEY="your_mistral_api_key_here"
```

## Development

To contribute to this project:

1. Clone the repository
2. Install in development mode: `pip install -e .`
3. Run tests: `python -m pytest tests/`

## License

MIT License - see LICENSE file for details.
