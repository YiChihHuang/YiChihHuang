"""
Abstract Base Class for LLM Providers
=====================================

Defines the interface that all LLM providers must implement.
Uses the Adapter Pattern for flexibility.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Union
from pathlib import Path


@dataclass
class LLMResponse:
    """Standard response format from LLM providers."""
    content: str
    model: str
    usage: Optional[dict] = None
    raw_response: Optional[object] = None


@dataclass
class VisionInput:
    """Input for vision-based requests."""
    image_path: Path
    prompt: str


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Implements the Adapter Pattern to allow seamless switching
    between different AI model providers (Gemini, OpenAI, Anthropic, etc.)
    """

    @abstractmethod
    def __init__(self, config: dict):
        """
        Initialize the provider with configuration.

        Args:
            config: Provider-specific configuration dictionary
        """
        pass

    @abstractmethod
    def text_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate text response from a prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    def vision_analyze(
        self,
        image_path: Union[Path, str],
        prompt: str,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Analyze an image with a prompt (Vision mode).

        Args:
            image_path: Path to the image file
            prompt: The analysis prompt
            temperature: Sampling temperature

        Returns:
            LLMResponse with analysis result
        """
        pass

    @abstractmethod
    def vision_analyze_multiple(
        self,
        image_paths: List[Union[Path, str]],
        prompt: str,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Analyze multiple images with a prompt.

        Args:
            image_paths: List of paths to image files
            prompt: The analysis prompt
            temperature: Sampling temperature

        Returns:
            LLMResponse with analysis result
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass

    @property
    @abstractmethod
    def supports_search(self) -> bool:
        """Return whether this provider supports search grounding."""
        pass
