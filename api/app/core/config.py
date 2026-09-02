from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    project_name: str = "ZambeCare"
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./zambecare.db"
    secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [value.strip() for value in self.allowed_origins.split(",") if value.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
