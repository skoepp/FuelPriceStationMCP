"""Application configuration via pydantic-settings with .env loading."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables with FUEL_MCP_ prefix."""

    model_config = SettingsConfigDict(
        env_prefix="FUEL_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    tankerkoenig_api_key: str = ""
    log_level: str = "INFO"
    default_radius_km: float = 15.0
    tankerkoenig_base_url: str = "https://creativecommons.tankerkoenig.de/json"
    request_timeout_seconds: float = 10.0
    demo_mode: bool = False
    demo_scenario: str = "default"


def get_settings() -> Settings:
    """Create and return application settings."""
    return Settings()
