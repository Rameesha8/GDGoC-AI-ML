from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


database_url: str = Field(..., validation_alias="DATABASE_URL")
qdrant_url: str = Field(..., validation_alias="QDRANT_URL")


class Settings(BaseSettings):
    """
    Central configuration object.

    Values are loaded from:
    1) environment variables
    2) .env file (for local development)

    Strong typing + validation prevents silent misconfiguration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="FastAPI App", validation_alias="APP_NAME")
    environment: str = Field(default="dev", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=False, validation_alias="DEBUG")

    host: str = Field(default="127.0.0.1", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")

    # Example secret. In real projects, treat this as sensitive.
    api_key: str = Field(..., validation_alias="API_KEY")

    database_url: str
    qdrant_url: str

    # Comma-separated list in .env -> parsed into list[str]
    allowed_origins_raw: str = Field(default="", validation_alias="ALLOWED_ORIGINS")

    @property
    def allowed_origins(self) -> List[str]:
        raw = self.allowed_origins_raw.strip()
        if not raw:
            return []
        return [x.strip() for x in raw.split(",") if x.strip()]


@lru_cache()
def get_settings() -> Settings:
    # Cached so Settings is created once.
    return Settings()
