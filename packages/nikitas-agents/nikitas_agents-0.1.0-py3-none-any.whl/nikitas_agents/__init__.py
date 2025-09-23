"""nikitas-agents: Provider-agnostic LLM agent abstractions."""

from .agents import BaseAgent
from . import schema

__version__ = "0.1.0"
__all__ = ["BaseAgent", "schema"]
