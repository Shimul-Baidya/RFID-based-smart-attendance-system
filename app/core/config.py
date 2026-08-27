"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Database and attendance-report settings."""

    database_url: str = (
        "postgresql+asyncpg://attendance:attendance@localhost:5432/"
        "rfid_attendance"
    )
    attendance_threshold: float = 75.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()
