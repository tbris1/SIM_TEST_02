"""
Application configuration and settings.
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    # Application metadata
    app_name: str = "Medical On-Call Simulation API"
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS settings
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # File paths
    scenarios_dir: Path = Path(__file__).parent.parent.parent / "data" / "scenarios"

    # Session settings
    session_timeout_minutes: int = 180  # 3 hours
    max_active_sessions: int = 100

    # OpenAI settings (for future phases)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
