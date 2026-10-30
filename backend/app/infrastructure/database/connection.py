"""PostgreSQL connection factory and readiness probe targeting the private lms schema.

Implements least-privilege runtime connection management with explicit SET ROLE
execution outside transaction blocks, preventing transaction nesting bugs and
ensuring atomic commit and rollback behavior.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path
from typing import Any

import psycopg
from pydantic import SecretStr

AsyncConnectionFactory = Callable[[], AbstractAsyncContextManager[psycopg.AsyncConnection[Any]]]


class PostgresProbe:
    """Readiness probe that checks database connectivity and lms schema readiness."""

    def __init__(self, dsn: SecretStr, sslrootcert: Path | None = None) -> None:
        self._dsn = dsn
        self._sslrootcert = sslrootcert

    async def ping(self) -> bool:
        """Verify database connectivity, schema availability and query capability."""
        try:
            conninfo_dict = psycopg.conninfo.conninfo_to_dict(self._dsn.get_secret_value())
            sslmode = conninfo_dict.get("sslmode") or (
                "verify-full"
                if self._sslrootcert
                or (conninfo_dict.get("host") not in ("127.0.0.1", "localhost", None))
                else "prefer"
            )
            conninfo_str = psycopg.conninfo.make_conninfo(
                self._dsn.get_secret_value(),
                connect_timeout=3,
                sslmode=sslmode,
                sslrootcert=str(self._sslrootcert) if self._sslrootcert else None,
            )
            # Health checks must not hold a web request open indefinitely.
            async with asyncio.timeout(5):
                connection = await psycopg.AsyncConnection.connect(
                    conninfo_str,
                    autocommit=True,
                )
                async with connection:
                    cursor = await connection.execute("SELECT 1 FROM lms.programs LIMIT 1")
                    await cursor.fetchone()
                    return True
        except (psycopg.Error, TimeoutError, OSError):
            # Connection errors can contain credentials or host details.
            return False


@asynccontextmanager
async def make_api_connection(
    dsn: SecretStr,
    sslrootcert: Path | None = None,
) -> AsyncIterator[psycopg.AsyncConnection[Any]]:
    """Open a PostgreSQL connection under the restricted lms_api role.

    Uses autocommit=True so SET ROLE does not leave an open transaction,
    allowing repository-level transactions to control commit and rollback
    boundaries explicitly.
    """
    conninfo_dict = psycopg.conninfo.conninfo_to_dict(dsn.get_secret_value())
    sslmode = conninfo_dict.get("sslmode") or (
        "verify-full"
        if sslrootcert or (conninfo_dict.get("host") not in ("127.0.0.1", "localhost", None))
        else "prefer"
    )
    conninfo_str = psycopg.conninfo.make_conninfo(
        dsn.get_secret_value(),
        connect_timeout=5,
        sslmode=sslmode,
        sslrootcert=str(sslrootcert) if sslrootcert else None,
    )
    connection = await psycopg.AsyncConnection.connect(
        conninfo_str,
        autocommit=True,
    )
    try:
        await connection.execute("SET ROLE lms_api;")
        yield connection
    finally:
        await connection.close()


def create_connection_factory(
    dsn: SecretStr,
    sslrootcert: Path | None = None,
) -> AsyncConnectionFactory:
    """Return an async context-manager factory returning an lms_api connection."""
    return lambda: make_api_connection(dsn, sslrootcert)
