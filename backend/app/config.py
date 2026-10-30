"""Load backend-only configuration independently of the working directory."""

from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LMS_",
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    environment: Literal["development", "test", "production"] = "development"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    database_url: SecretStr | None = None
    database_sslrootcert: Path | None = None

    # Public submission protections (see docs/operations/public-submission-protection.md).
    # Counters live in one worker process; an edge proxy/WAF must provide the
    # authoritative limit when more than one worker or instance serves traffic.
    # Set submission_rate_limit to 0 to disable the in-process limiter.
    submission_rate_limit: int = Field(default=10, ge=0)
    submission_rate_window_seconds: int = Field(default=60, ge=1)
    max_request_body_bytes: int = Field(default=16384, ge=1024)

    @field_validator("database_url", "database_sslrootcert", mode="before")
    @classmethod
    def empty_value_is_unconfigured(cls, value: object) -> object:
        return None if isinstance(value, str) and not value.strip() else value

    @field_validator("database_url")
    @classmethod
    def require_postgres_url(cls, value: SecretStr | None) -> SecretStr | None:
        if value is not None:
            parsed = urlsplit(value.get_secret_value())
            if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname:
                raise ValueError("Use a PostgreSQL connection URL")
        return value

    @field_validator("cors_origins")
    @classmethod
    def require_explicit_origins(cls, values: list[str]) -> list[str]:
        origins: list[str] = []
        for value in values:
            parsed = urlsplit(value)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or "*" in value
                or parsed.username
                or parsed.password
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("CORS requires explicit HTTP(S) origins")
            origins.append(value.rstrip("/"))
        return origins
