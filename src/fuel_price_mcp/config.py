"""Application configuration via pydantic-settings with .env loading.

Two usage modes:
- Local development (make dev): settings are loaded from a .env file in the
  project root (CWD-relative). Set FUEL_MCP_DEMO_MODE=true there to use mock
  data without hitting the real API.
- MCP server (Claude Desktop etc.): the host passes FUEL_MCP_TANKERKOENIG_API_KEY
  and other vars directly as process environment variables. No .env file is
  needed or expected. Demo mode auto-activates when no API key is present.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables with FUEL_MCP_ prefix."""

    model_config = SettingsConfigDict(
        env_prefix="FUEL_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        # Treat empty strings as unset so a missing env var in the MCP host
        # config doesn't accidentally override a .env value or the default.
        env_ignore_empty=True,
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
