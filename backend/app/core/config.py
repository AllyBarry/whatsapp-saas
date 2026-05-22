"""Application configuration loaded from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://whatsapp:whatsapp@localhost:5432/whatsapp_saas"

    # Auth
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720

    # Encryption
    encryption_key: str = "change-me"

    # Meta WhatsApp Cloud API
    meta_graph_version: str = "v22.0"
    meta_graph_base_url: str = "https://graph.facebook.com"

    # App
    environment: str = "development"
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    # Redis (queue-ready, optional)
    redis_url: str = "redis://localhost:6379/0"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def meta_api_base(self) -> str:
        return f"{self.meta_graph_base_url}/{self.meta_graph_version}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
