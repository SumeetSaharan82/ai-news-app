"""
Application settings and configuration management
"""

from typing import List
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App Configuration
    app_name: str = Field(default="AI News App", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Server Configuration
    server_host: str = Field(default="0.0.0.0", env="SERVER_HOST")
    server_port: int = Field(default=8000, env="SERVER_PORT")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], env="CORS_ORIGINS"
    )

    # API Keys
    newsapi_key: str = Field(default="", env="NEWSAPI_KEY")
    nyt_api_key: str = Field(default="", env="NYT_API_KEY")
    guardian_api_key: str = Field(default="", env="GUARDIAN_API_KEY")

    # LLM Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")

    # Database Configuration
    database_url: str = Field(default="sqlite:///./news_app.db", env="DATABASE_URL")
    sqlalchemy_echo: bool = Field(default=False, env="SQLALCHEMY_ECHO")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_enabled: bool = Field(default=True, env="REDIS_ENABLED")

    # Cache Settings
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # seconds
    news_fetch_interval: int = Field(default=1800, env="NEWS_FETCH_INTERVAL")  # seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Load and cache settings
    Returns:
        Settings: Application settings instance
    """
    return Settings()
