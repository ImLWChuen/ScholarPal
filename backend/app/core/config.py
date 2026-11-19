from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "ScholarPal API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "scholarpal"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/scholarpal"

    # Operational & Startup flags
    RUN_MIGRATIONS: bool = False
    SEED_DATA: bool = False
    SCHEDULER_INTERVAL_SECONDS: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Security
    SECRET_KEY: str = "change-this-in-production-super-secret-key-at-least-32-bytes-long"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # External AI Providers (LLM + Jev)
    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gemini-1.5-pro"
    JEV_API_KEY: str | None = None

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @model_validator(mode="before")
    @classmethod
    def assemble_database_url(cls, values: dict[str, Any]) -> dict[str, Any]:
        if isinstance(values, dict):
            # If POSTGRES_SERVER is set and DATABASE_URL is not customized
            db_url = values.get("DATABASE_URL")
            server = values.get("POSTGRES_SERVER")
            if server and (not db_url or "localhost" in db_url):
                user = values.get("POSTGRES_USER", "postgres")
                pwd = values.get("POSTGRES_PASSWORD", "postgres")
                port = values.get("POSTGRES_PORT", 5432)
                db = values.get("POSTGRES_DB", "scholarpal")
                values["DATABASE_URL"] = f"postgresql+asyncpg://{user}:{pwd}@{server}:{port}/{db}"
        return values


settings = Settings()
