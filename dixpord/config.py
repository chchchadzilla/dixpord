"""
config.py - Configuration management for Dixpord.
Loads settings from .env and provides defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Config:
    """Central configuration for the Dixpord exporter."""

    # Discord Bot Token (optional — needed for bot mode)
    BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")

    # Discord User Token (optional — needed for user mode / DM access)
    USER_TOKEN: str = os.getenv("DISCORD_USER_TOKEN", "")

    # GitHub credentials (optional, for contributors)
    GITHUB_USER: str = os.getenv("GITHUB_USER_NAME", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", os.getenv("GITHUB_MAGIC", ""))

    # Discord login creds (stored for user reference, not used by the tool)
    DISCORD_USER: str = os.getenv("DISCORD_USER_NAME", "")

    # Export settings
    EXPORT_DIR: str = os.getenv("EXPORT_DIR", "./exports")
    DEFAULT_FORMAT: str = os.getenv("DEFAULT_FORMAT", "txt").lower()
    FETCH_LIMIT: int = int(os.getenv("FETCH_LIMIT", "100"))

    # Supported export formats
    SUPPORTED_FORMATS = ("txt", "md", "pdf")

    # Rate-limit safety delay (seconds) between large fetches
    RATE_LIMIT_DELAY: float = 0.5

    @classmethod
    def has_user_token(cls) -> bool:
        return bool(cls.USER_TOKEN) and cls.USER_TOKEN != "YOUR_USER_TOKEN_HERE"

    @classmethod
    def has_bot_token(cls) -> bool:
        return bool(cls.BOT_TOKEN) and cls.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE"

    @classmethod
    def validate(cls) -> list[str]:
        """Return a list of configuration problems (empty = all good)."""
        problems = []
        if not cls.has_bot_token() and not cls.has_user_token():
            problems.append(
                "No Discord token found. Set at least one of:\n"
                "  • DISCORD_USER_TOKEN  — for user mode (DMs, personal messages)\n"
                "  • DISCORD_BOT_TOKEN   — for bot mode\n"
                "Copy .env.example to .env and fill in your token(s)."
            )
        if cls.DEFAULT_FORMAT not in cls.SUPPORTED_FORMATS:
            problems.append(
                f"DEFAULT_FORMAT '{cls.DEFAULT_FORMAT}' is invalid. "
                f"Use one of: {', '.join(cls.SUPPORTED_FORMATS)}"
            )
        return problems

    @classmethod
    def ensure_export_dir(cls) -> Path:
        """Create and return the export directory."""
        path = Path(cls.EXPORT_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
