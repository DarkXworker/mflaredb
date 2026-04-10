import base64
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    HMAC_SECRET: str = Field(..., env="HMAC_SECRET")
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # TMDB
    TMDB_API_KEY: str = Field(default="", env="TMDB_API_KEY")
    TMDB_BASE_URL: str = Field(default="https://api.themoviedb.org/3", env="TMDB_BASE_URL")
    TMDB_IMAGE_BASE: str = Field(default="https://image.tmdb.org/t/p/original", env="TMDB_IMAGE_BASE")

    # Admin
    ADMIN_USERNAME: str = Field(default="admin", env="ADMIN_USERNAME")
    ADMIN_PASSWORD: str = Field(..., env="ADMIN_PASSWORD")
    ADMIN_SECRET_KEY: str = Field(..., env="ADMIN_SECRET_KEY")

    # App
    APP_ENV: str = Field(default="production", env="APP_ENV")
    APP_HOST: str = Field(default="0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(default=8000, env="APP_PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Security Toggles
    IP_WHITELIST_ENABLED: bool = Field(default=False, env="IP_WHITELIST_ENABLED")
    REQUIRE_DEVICE_HASH: bool = Field(default=True, env="REQUIRE_DEVICE_HASH")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")

    # Token
    STREAM_TOKEN_EXPIRY_SECONDS: int = Field(default=60, env="STREAM_TOKEN_EXPIRY_SECONDS")
    CACHE_TTL_HOME: int = Field(default=300, env="CACHE_TTL_HOME")

    def get_encryption_key_bytes(self) -> bytes:
        """Returns 32-byte AES key from base64 string"""
        key = self.ENCRYPTION_KEY
        try:
            decoded = base64.b64decode(key)
            if len(decoded) != 32:
                raise ValueError("Encryption key must be 32 bytes after base64 decode")
            return decoded
        except Exception:
            # Derive 32 bytes directly if not base64
            return key.encode()[:32].ljust(32, b'0')

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
