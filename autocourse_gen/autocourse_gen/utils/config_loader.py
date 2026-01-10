"""
Configuration Loader
====================

Loads and manages configuration from config.yaml and .env files.
"""

import os
from pathlib import Path
from typing import Optional, Any

import yaml
from dotenv import load_dotenv


class ConfigLoader:
    """
    Singleton configuration loader.

    Loads configuration from:
    1. .env file (for API keys and secrets)
    2. config.yaml (for application settings)
    """

    _instance: Optional["ConfigLoader"] = None
    _config: Optional[dict] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_config()

    def _find_project_root(self) -> Path:
        """Find the project root directory (where config.yaml is)."""
        current = Path(__file__).parent

        # Walk up to find config.yaml
        for _ in range(5):
            if (current / "config.yaml").exists():
                return current
            if (current.parent / "config.yaml").exists():
                return current.parent
            current = current.parent

        # Default to current working directory
        return Path.cwd()

    def _load_config(self):
        """Load configuration from files."""
        project_root = self._find_project_root()

        # Load .env file
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # Try parent directory
            parent_env = project_root.parent / ".env"
            if parent_env.exists():
                load_dotenv(parent_env)

        # Load config.yaml
        config_path = project_root / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
        else:
            # Use default configuration
            self._config = self._default_config()

        # Set project root in config
        self._config["_project_root"] = str(project_root)

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            "llm": {
                "default_provider": "gemini",
                "gemini": {
                    "text_model": "gemini-1.5-pro",
                    "vision_model": "gemini-1.5-pro",
                    "temperature": 0.7,
                    "max_tokens": 8192,
                    "enable_search": True,
                },
            },
            "tts": {
                "voice": "zh-TW-HsiaoChenNeural",
                "rate": "+0%",
                "volume": "+0%",
            },
            "video": {
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "background_color": "#FFFFFF",
            },
            "slides": {
                "width_inches": 13.333,
                "height_inches": 7.5,
                "primary_color": "#2B579A",
                "secondary_color": "#5B9BD5",
                "accent_color": "#ED7D31",
                "title_font": "Microsoft JhengHei",
                "body_font": "Microsoft JhengHei",
                "code_font": "Consolas",
            },
            "cursor": {
                "image": "cursor.png",
                "size": 32,
                "bezier_steps": 60,
                "speed_factor": 1.0,
            },
            "workspace": {
                "output_dir": "workspace",
                "resumable": True,
                "ask_before_skip": True,
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key (e.g., "llm.gemini.temperature")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_section(self, section: str) -> dict:
        """
        Get an entire configuration section.

        Args:
            section: Section name (e.g., "llm", "tts")

        Returns:
            Configuration section as dict
        """
        return self._config.get(section, {})

    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(self._config.get("_project_root", "."))

    @property
    def workspace_dir(self) -> Path:
        """Get the workspace directory path."""
        output_dir = self.get("workspace.output_dir", "workspace")
        return self.project_root / output_dir

    def ensure_workspace(self) -> Path:
        """Ensure workspace directory exists and return its path."""
        workspace = self.workspace_dir
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace


# Global config instance
_config: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = ConfigLoader()
    return _config
