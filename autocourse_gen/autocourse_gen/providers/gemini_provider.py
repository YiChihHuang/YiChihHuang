"""
Google Gemini Provider Implementation
=====================================

Implements the LLMProvider interface for Google's Gemini API.
Supports both text and vision modes.
"""

import os
import base64
from pathlib import Path
from typing import Optional, List, Union

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .base import LLMProvider, LLMResponse


class GeminiProvider(LLMProvider):
    """
    Google Gemini API provider implementation.

    Supports:
    - Text generation (gemini-1.5-pro, gemini-1.5-flash)
    - Vision analysis (gemini-1.5-pro with image input)
    - Search grounding (when available)
    """

    def __init__(self, config: dict):
        """
        Initialize Gemini provider.

        Args:
            config: Configuration dictionary with Gemini settings
        """
        self.config = config
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )

        # Configure the API
        genai.configure(api_key=self.api_key)

        # Model settings
        self.text_model_name = config.get("text_model", "gemini-1.5-pro")
        self.vision_model_name = config.get("vision_model", "gemini-1.5-pro")
        self.default_temperature = config.get("temperature", 0.7)
        self.default_max_tokens = config.get("max_tokens", 8192)
        self.enable_search = config.get("enable_search", True)

        # Safety settings (relaxed for educational content)
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        # Initialize models
        self._text_model = None
        self._vision_model = None

    @property
    def text_model(self):
        """Lazy initialization of text model."""
        if self._text_model is None:
            generation_config = genai.GenerationConfig(
                temperature=self.default_temperature,
                max_output_tokens=self.default_max_tokens,
            )
            self._text_model = genai.GenerativeModel(
                model_name=self.text_model_name,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
            )
        return self._text_model

    @property
    def vision_model(self):
        """Lazy initialization of vision model."""
        if self._vision_model is None:
            generation_config = genai.GenerationConfig(
                temperature=self.default_temperature,
                max_output_tokens=self.default_max_tokens,
            )
            self._vision_model = genai.GenerativeModel(
                model_name=self.vision_model_name,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
            )
        return self._vision_model

    def text_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate text using Gemini.

        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            LLMResponse with generated content
        """
        # Build the full prompt
        full_prompt = ""
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
        else:
            full_prompt = prompt

        # Override generation config if needed
        generation_config = None
        if temperature is not None or max_tokens is not None:
            generation_config = genai.GenerationConfig(
                temperature=temperature or self.default_temperature,
                max_output_tokens=max_tokens or self.default_max_tokens,
            )

        try:
            # Generate response
            if generation_config:
                response = self.text_model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                )
            else:
                response = self.text_model.generate_content(full_prompt)

            # Extract content
            content = response.text if response.text else ""

            # Build usage info
            usage = None
            if hasattr(response, 'usage_metadata'):
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }

            return LLMResponse(
                content=content,
                model=self.text_model_name,
                usage=usage,
                raw_response=response,
            )

        except Exception as e:
            raise RuntimeError(f"Gemini text generation failed: {str(e)}")

    def _load_image(self, image_path: Union[Path, str]) -> dict:
        """Load an image file for Gemini API."""
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        # Determine MIME type
        suffix = path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_types.get(suffix, "image/png")

        # Read and encode image
        with open(path, "rb") as f:
            image_data = f.read()

        return {
            "mime_type": mime_type,
            "data": image_data,
        }

    def vision_analyze(
        self,
        image_path: Union[Path, str],
        prompt: str,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Analyze an image using Gemini Vision.

        Args:
            image_path: Path to the image file
            prompt: The analysis prompt
            temperature: Override default temperature

        Returns:
            LLMResponse with analysis result
        """
        return self.vision_analyze_multiple([image_path], prompt, temperature)

    def vision_analyze_multiple(
        self,
        image_paths: List[Union[Path, str]],
        prompt: str,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Analyze multiple images using Gemini Vision.

        Args:
            image_paths: List of paths to image files
            prompt: The analysis prompt
            temperature: Override default temperature

        Returns:
            LLMResponse with analysis result
        """
        # Load all images
        images = [self._load_image(path) for path in image_paths]

        # Build content parts
        content_parts = []
        for img in images:
            content_parts.append({
                "inline_data": img
            })
        content_parts.append(prompt)

        # Override generation config if needed
        generation_config = None
        if temperature is not None:
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=self.default_max_tokens,
            )

        try:
            # Generate response
            if generation_config:
                response = self.vision_model.generate_content(
                    content_parts,
                    generation_config=generation_config,
                )
            else:
                response = self.vision_model.generate_content(content_parts)

            # Extract content
            content = response.text if response.text else ""

            # Build usage info
            usage = None
            if hasattr(response, 'usage_metadata'):
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }

            return LLMResponse(
                content=content,
                model=self.vision_model_name,
                usage=usage,
                raw_response=response,
            )

        except Exception as e:
            raise RuntimeError(f"Gemini vision analysis failed: {str(e)}")

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "gemini"

    @property
    def supports_search(self) -> bool:
        """Return whether search grounding is enabled."""
        return self.enable_search
