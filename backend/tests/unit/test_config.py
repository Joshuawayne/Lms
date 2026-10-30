"""Check secret handling and origin configuration before startup."""

import pytest
from pydantic import SecretStr, ValidationError

from app.config import Settings


def test_blank_database_values_are_unconfigured() -> None:
    settings = Settings(_env_file=None, database_url="", database_sslrootcert="")
    assert settings.database_url is None
    assert settings.database_sslrootcert is None


def test_database_secret_is_masked_in_settings_representation() -> None:
    settings = Settings(
        _env_file=None,
        database_url=SecretStr("postgresql://example:private-password@db.example/postgres"),
    )
    assert "private-password" not in repr(settings)


@pytest.mark.parametrize("origin", ["*", "https://*.example.com", "https://example.com/path"])
def test_wildcard_or_path_origins_are_rejected(origin: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins=[origin])
