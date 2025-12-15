"""
BlueSky CLI Utilities
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from rich.console import Console

# Constants
APP_NAME = "bluesky-cli"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CACHE_DIR = Path.home() / ".cache" / APP_NAME
LOG_DIR = Path.home() / ".local" / "share" / APP_NAME

# Ensure directories exist
for directory in [CONFIG_DIR, CACHE_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = CONFIG_DIR / "config.json"

console = Console()

# Supported AI providers
PROVIDERS = {
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini"
    },
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-3-haiku-20240307"
    },
    "ollama": {
        "env_key": None,  # No API key needed
        "base_url": "http://localhost:11434/v1",
        "default_model": "llama3.2"
    }
}


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment."""
    config = {}

    # Load from file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass

    # Environment variables override file config
    if os.getenv("OPENAI_API_KEY"):
        config["openai_api_key"] = os.getenv("OPENAI_API_KEY")

    if os.getenv("ANTHROPIC_API_KEY"):
        config["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY")

    if os.getenv("AI_PROVIDER"):
        config["ai_provider"] = os.getenv("AI_PROVIDER")

    if os.getenv("BSKY_IDENTIFIER"):
        config["bsky_identifier"] = os.getenv("BSKY_IDENTIFIER")

    if os.getenv("BSKY_PASSWORD"):
        config["bsky_password"] = os.getenv("BSKY_PASSWORD")

    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_ai_provider() -> str:
    """Get the configured AI provider (openai, anthropic, or ollama)."""
    config = load_config()
    provider = config.get("ai_provider", "openai").lower()

    # Validate provider
    if provider not in PROVIDERS:
        return "openai"
    return provider


def get_ai_api_key() -> Optional[str]:
    """Get the API key for the configured provider."""
    config = load_config()
    provider = get_ai_provider()

    if provider == "ollama":
        return "ollama"  # No key needed, return placeholder

    # Check config first, then environment
    key_name = f"{provider}_api_key"
    if key_name in config:
        return config[key_name]

    env_key = PROVIDERS[provider]["env_key"]
    return os.getenv(env_key) if env_key else None


def get_ai_config() -> Dict[str, Any]:
    """Get full AI configuration for the current provider."""
    provider = get_ai_provider()
    api_key = get_ai_api_key()

    return {
        "provider": provider,
        "api_key": api_key,
        "base_url": PROVIDERS[provider]["base_url"],
        "model": PROVIDERS[provider]["default_model"]
    }


def get_bsky_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Get BlueSky credentials (identifier, password)."""
    config = load_config()
    return config.get("bsky_identifier"), config.get("bsky_password")
