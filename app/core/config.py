from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    database_url: SecretStr
    cors_origins: list[str] = ["http://localhost:4200", "http://127.0.0.1:4200"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
