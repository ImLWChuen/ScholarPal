from pathlib import Path
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/scholarpal"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR / ".env",
            BACKEND_DIR / ".env",
        ),
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
    DATABASE_URL: str = DEFAULT_DATABASE_URL

    # Operational & Startup flags
    RUN_MIGRATIONS: bool = False
    SEED_DATA: bool = False
    SCHEDULER_INTERVAL_SECONDS: int = Field(default=60, ge=1)

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
            server = values.get("POSTGRES_SERVER")
            db_url = values.get("DATABASE_URL")

            if server:
                is_default = (not db_url) or (db_url == DEFAULT_DATABASE_URL)
                is_localhost = False
                if db_url and not is_default:
                    try:
                        parsed = make_url(db_url)
                        is_localhost = parsed.host in ("localhost", "127.0.0.1")
                    except Exception:
                        pass

                if is_default or is_localhost:
                    user = values.get("POSTGRES_USER", "postgres")
                    pwd = values.get("POSTGRES_PASSWORD", "postgres")
                    port = values.get("POSTGRES_PORT", 5432)
                    db = values.get("POSTGRES_DB", "scholarpal")
                    url = URL.create(
                        drivername="postgresql+asyncpg",
                        username=user,
                        password=pwd,
                        host=server,
                        port=int(port) if port else None,
                        database=db,
                    )
                    values["DATABASE_URL"] = url.render_as_string(hide_password=False)

        return values


settings = Settings()
