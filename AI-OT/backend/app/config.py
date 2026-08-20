"""Environment-based application settings."""
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "AI-OT"
    environment: str = "development"
    database_url: str = "sqlite:///./aiot_dev.db"
    jwt_secret_key: str = "local-dev-secret"
    jwt_access_token_expire_minutes: int = 60
    demo_seed_password: str = "123456"
    frontend_origin: str = "http://localhost:5173"
    image_storage_path: str = "./app/uploads/images"
    ai_api_key: str | None = None
    ai_api_base_url: str | None = None
    ai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="before")
    @classmethod
    def strip_placeholder_environment_values(cls, data):
        if not isinstance(data, dict):
            return data

        for key in ("database_url", "jwt_secret_key", "demo_seed_password", "frontend_origin"):
            value = data.get(key)
            if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                data.pop(key, None)
        return data


@lru_cache
def get_settings() -> Settings:
    return Settings()
