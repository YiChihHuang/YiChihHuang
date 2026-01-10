"""
LLM Providers Module
====================

Implements the Adapter Pattern for LLM providers,
allowing easy switching between different AI models.
"""

from .base import LLMProvider
from .gemini_provider import GeminiProvider

__all__ = ["LLMProvider", "GeminiProvider"]
