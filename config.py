from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file"""

    # Environment control
    environment: str = Field(
        default="production",
        validation_alias="ENVIRONMENT",
        description="Runtime environment (development/production)",
    )

    # Vianexus API configuration
    vianexus_api_key: str = Field(
        default="RETRIVE_FROM_ENV",
        validation_alias="VIANEXUS_API_KEY",
        description="API key for Vianexus API",
    )
    vianexus_base_url: str = Field(
        default="https://api.blueskyapi.com/v1",
        validation_alias="VIANEXUS_BASE_URL",
        description="Base URL for Vianexus API",
    )

    # Logging configuration
    log_level: str = Field(
        default="DEBUG",
        validation_alias="LOG_LEVEL",
        description="Root logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Module-specific log levels (comma-separated KEY:VALUE pairs)
    # Example: "httpx:WARNING,httpcore:WARNING,urllib3:WARNING"
    module_log_levels: str = Field(
        default="httpx:WARNING,httpcore:WARNING",
        validation_alias="MODULE_LOG_LEVELS",
        description="Module-specific log levels as comma-separated pairs (module:level)",
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


# Singleton instance
settings = Settings()
