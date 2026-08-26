# Core configuration for the project
"""Configuration module.

Loads environment variables (or defaults) that are required for the JWT
authentication flow.  Pydantic's ``BaseSettings`` makes it easy to keep the
settings type‑safe while still allowing overrides from a ``.env`` file.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Secret key used to sign JWT tokens – keep this secret in production!
    JWT_SECRET_KEY: str = "your_secret_key_here"
    # Algorithm for JWT encoding/decoding – HS256 is a sensible default.
    JWT_ALGORITHM: str = "HS256"
    # Access token expiry in minutes (default 60).  Adjust as needed for the
    # academic demo; a short-lived token is easier to test.
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        # Load variables from a .env file located at the project root.
        env_file = ".env"
        env_file_encoding = "utf-8"

# A singleton instance that can be imported throughout the codebase.
settings = Settings()

