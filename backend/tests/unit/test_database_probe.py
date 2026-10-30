"""The readiness probe must enforce TLS and contain connection failures."""

import asyncio
from unittest.mock import AsyncMock, patch

import psycopg
from pydantic import SecretStr

from app.infrastructure.database.connection import PostgresProbe


def test_connection_failure_is_reported_without_propagating_driver_details() -> None:
    connect = AsyncMock(side_effect=psycopg.OperationalError("secret-in-driver-message"))
    with patch("psycopg.AsyncConnection.connect", connect):
        result = asyncio.run(PostgresProbe(SecretStr("postgresql://db.example/db")).ping())
    assert result is False
    options = psycopg.conninfo.conninfo_to_dict(connect.call_args.args[0])
    assert options["sslmode"] == "verify-full"
    assert options["connect_timeout"] == "3"
