"""Application settings using Pydantic."""

import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =============================================================================
    # Database
    # =============================================================================
    database_url: str = Field(
        default="sqlite:///./data/job_intelligence.db",
        description="Database connection URL",
    )

    # =============================================================================
    # Application
    # =============================================================================
    app_env: str = Field(default="development", description="Application environment")
    secret_key: str = Field(default="change-me-in-production", description="Secret key")
    debug: bool = Field(default=True, description="Debug mode")

    # =============================================================================
    # API Keys
    # =============================================================================
    openai_api_key: str = Field(default="", description="OpenAI API key")
    linkedin_client_id: str = Field(default="", description="LinkedIn client ID")
    linkedin_client_secret: str = Field(default="", description="LinkedIn client secret")

    # =============================================================================
    # Scraping
    # =============================================================================
    scrape_rate_limit: int = Field(default=1, description="Requests per second")
    scrape_max_retries: int = Field(default=3, description="Max retries per request")
    scrape_timeout: int = Field(default=30, description="Request timeout in seconds")
    enable_indeed_scraper: bool = Field(default=True, description="Enable Indeed scraper")
    enable_glints_scraper: bool = Field(default=True, description="Enable Glints scraper")
    enable_jobstreet_scraper: bool = Field(default=True, description="Enable JobStreet scraper")
    enable_linkedin_scraper: bool = Field(default=False, description="Enable LinkedIn scraper")

    # =============================================================================
    # ML Models
    # =============================================================================
    hf_token: str = Field(default="", description="HuggingFace token")
    skill_matching_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Model for skill matching embeddings",
    )
    job_classifier_model: str = Field(
        default="facebook/bart-large-mnli",
        description="Model for job classification",
    )

    # =============================================================================
    # Email
    # =============================================================================
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_user: str = Field(default="", description="SMTP user")
    smtp_password: str = Field(default="", description="SMTP password")
    report_recipient: str = Field(default="", description="Report recipient email")

    # =============================================================================
    # Logging
    # =============================================================================
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="logs/app.log", description="Log file path")

    # =============================================================================
    # Computed Properties
    # =============================================================================
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env.lower() == "development"

    @property
    def scraping_enabled(self) -> bool:
        """Check if any scraper is enabled."""
        return (
            self.enable_indeed_scraper
            or self.enable_glints_scraper
            or self.enable_jobstreet_scraper
            or self.enable_linkedin_scraper
        )

    @property
    def enabled_scrapers(self) -> List[str]:
        """Get list of enabled scrapers."""
        scrapers = []
        if self.enable_indeed_scraper:
            scrapers.append("indeed")
        if self.enable_glints_scraper:
            scrapers.append("glints")
        if self.enable_jobstreet_scraper:
            scrapers.append("jobstreet")
        if self.enable_linkedin_scraper:
            scrapers.append("linkedin")
        return scrapers


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()