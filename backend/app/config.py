"""
Configuration module - loads environment variables and secrets.
DO NOT commit actual secrets to version control.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "ChatApp"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"  # TODO: Set via env

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/chatapp"

    # JWT
    JWT_SECRET: str = "jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 7  # 7 days

    # Redis (for async queue)
    REDIS_URL: str = "redis://localhost:6379/0"

    # GitHub (for storage backup)
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_REPO: Optional[str] = None  # e.g., "username/chat-storage"

    # HuggingFace (optional)
    HF_TOKEN: Optional[str] = None
    HF_SPACE_ID: Optional[str] = None

    # Compression settings
    COMPRESSION_ENABLED: bool = True
    MAX_BATCH_SIZE_MB: int = 10
    BATCH_INTERVAL_MINUTES: int = 60

    # Storage
    STORAGE_PATH: str = "./storage/data"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()