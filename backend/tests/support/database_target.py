"""Resolve and verify the isolated PostgreSQL target used by native database tests.

Design rules (see docs/testing/native-database-tests.md):
  * There is NO fallback to the ordinary runtime database URL.  Tests run only
    when LMS_TEST_DATABASE_URL and LMS_TEST_MAINTENANCE_DATABASE_URL are set.
  * The test database must be a dedicated database named ``lms_test`` or
    ``lms_test_<suffix>``, must differ from the runtime database, must never be a
    hosted Supabase endpoint, and must carry the marker comment written by
    ``scripts/db_tools.py create-test-db``.
  * Every one of those checks completes BEFORE any fixture is written.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import psycopg
from dotenv import dotenv_values

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_ROOT / ".env"

TEST_URL_VARIABLE = "LMS_TEST_DATABASE_URL"
MAINTENANCE_URL_VARIABLE = "LMS_TEST_MAINTENANCE_DATABASE_URL"
RUNTIME_URL_VARIABLE = "LMS_DATABASE_URL"
REQUIRE_VARIABLE = "LMS_REQUIRE_DATABASE_TESTS"

TEST_DATABASE_MARKER = "jjenga-lms-isolated-test-database"
_TEST_DATABASE_NAME = re.compile(r"^lms_test(_[a-z0-9]+)*$")
_HOSTED_SUPABASE_SUFFIXES = (".supabase.co", ".supabase.com", ".supabase.net")


class UnsafeTestTargetError(RuntimeError):
    """The configured test database could not be proven isolated from real data."""


@dataclass(frozen=True)
class DatabaseTarget:
    """Connection descriptors for the isolated test database (no secrets in repr)."""

    host: str
    port: int
    database: str
    api_url: str = ""
    maintenance_url: str = ""

    def __repr__(self) -> str:
        return f"DatabaseTarget(host={self.host!r}, port={self.port}, database={self.database!r})"

    def maintenance_url_for(self, database: str) -> str:
        """Maintenance credentials aimed at ``database`` on the same server."""
        return psycopg.conninfo.make_conninfo(self.maintenance_url, dbname=database)


def load_environment(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Merge backend/.env under process variables; the process environment wins."""
    merged: dict[str, str] = {
        key: value
        for key, value in dotenv_values(ENV_FILE).items()
        if value is not None and key.startswith("LMS_")
    }
    merged.update({k: v for k, v in (environ or os.environ).items() if k.startswith("LMS_")})
    return merged


def _endpoint(url: str) -> tuple[str, int, str]:
    info = psycopg.conninfo.conninfo_to_dict(url)
    return (
        str(info.get("host") or "localhost").lower(),
        int(info.get("port") or 5432),
        str(info.get("dbname") or ""),
    )


def resolve_target(environment: Mapping[str, str]) -> DatabaseTarget | None:
    """Return the verified-by-configuration target, ``None`` if tests are not configured.

    Raises UnsafeTestTargetError for any configuration that is set but unsafe.
    """
    api_url = environment.get(TEST_URL_VARIABLE, "").strip()
    maintenance_url = environment.get(MAINTENANCE_URL_VARIABLE, "").strip()
    if not api_url and not maintenance_url:
        return None
    if not api_url or not maintenance_url:
        raise UnsafeTestTargetError(
            f"Set both {TEST_URL_VARIABLE} and {MAINTENANCE_URL_VARIABLE}; "
            "there is no fallback to the runtime database."
        )

    host, port, database = _endpoint(api_url)
    maintenance_host, maintenance_port, _ = _endpoint(maintenance_url)

    if not _TEST_DATABASE_NAME.fullmatch(database):
        raise UnsafeTestTargetError(
            f"Test database name must be 'lms_test' or 'lms_test_<suffix>', got {database!r}."
        )
    if (host, port) != (maintenance_host, maintenance_port):
        raise UnsafeTestTargetError("Test and maintenance URLs must point at the same server.")
    if host.endswith(_HOSTED_SUPABASE_SUFFIXES) or "supabase" in host:
        raise UnsafeTestTargetError("Hosted Supabase endpoints are never valid test targets.")

    runtime_url = environment.get(RUNTIME_URL_VARIABLE, "").strip()
    if runtime_url and _endpoint(runtime_url) == (host, port, database):
        raise UnsafeTestTargetError("The test database is the same as the runtime database.")

    return DatabaseTarget(
        host=host, port=port, database=database, api_url=api_url, maintenance_url=maintenance_url
    )


def verify_target(target: DatabaseTarget) -> None:
    """Prove, on the live server, that this really is the dedicated test database.

    Runs before any fixture write.  Raises UnsafeTestTargetError otherwise.
    """
    try:
        with psycopg.connect(target.maintenance_url_for(target.database), autocommit=True) as conn:
            row = conn.execute(
                "SELECT current_database(), shobj_description(d.oid, 'pg_database') "
                "FROM pg_database d WHERE d.datname = current_database()"
            ).fetchone()
            has_schema = conn.execute("SELECT to_regclass('lms.programs') IS NOT NULL").fetchone()
    except psycopg.Error as error:
        raise UnsafeTestTargetError(
            f"Cannot reach test database {target.database!r}. Run "
            "`uv run --project backend python scripts/db_tools.py create-test-db`."
        ) from error

    if row is None or row[0] != target.database:
        raise UnsafeTestTargetError("Connected database does not match the configured test name.")
    if row[1] != TEST_DATABASE_MARKER:
        raise UnsafeTestTargetError(
            f"{target.database!r} lacks the isolated-test marker; refusing to write fixtures. "
            "Recreate it with scripts/db_tools.py create-test-db."
        )
    if has_schema is None or not has_schema[0]:
        raise UnsafeTestTargetError("The test database has no lms schema; apply the migrations.")
