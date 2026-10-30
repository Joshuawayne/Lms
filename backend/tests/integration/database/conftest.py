"""Fixtures for native PostgreSQL tests: isolated target, verified before writes, always cleaned.

The suite never falls back to the runtime database.  Without explicit configuration the
database tests are skipped with a visible reason; set LMS_REQUIRE_DATABASE_TESTS=1 (as the
project verification script does) to turn that skip into a failure.
"""

from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import Iterator

import psycopg
import pytest
from pydantic import SecretStr
from support.database_target import (
    REQUIRE_VARIABLE,
    DatabaseTarget,
    load_environment,
    resolve_target,
    verify_target,
)
from support.fixture_ledger import FIXTURE_SLUG_PREFIX, FixtureLedger

from app.infrastructure.database.connection import (
    AsyncConnectionFactory,
    create_connection_factory,
)

# psycopg's async driver cannot run on the Windows Proactor loop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Captured at import: the per-test environment isolation removes LMS_* variables later.
_ENVIRONMENT = load_environment()


@pytest.fixture(scope="session")
def database_target() -> Iterator[DatabaseTarget]:
    """Resolve and verify the isolated database before any test writes to it."""
    target = resolve_target(_ENVIRONMENT)
    if target is None:
        message = (
            "Native database tests need LMS_TEST_DATABASE_URL and "
            "LMS_TEST_MAINTENANCE_DATABASE_URL (an isolated lms_test database; see "
            "docs/testing/native-database-tests.md). They never use LMS_DATABASE_URL."
        )
        if os.environ.get(REQUIRE_VARIABLE, "").lower() in {"1", "true", "yes"}:
            pytest.fail(message, pytrace=False)
        pytest.skip(message)
    verify_target(target)

    yield target

    # Leak check: no fixture program may survive the session.
    with psycopg.connect(target.maintenance_url_for(target.database), autocommit=True) as conn:
        row = conn.execute(
            "SELECT count(*) FROM lms.programs WHERE slug LIKE %s", (f"{FIXTURE_SLUG_PREFIX}%",)
        ).fetchone()
    assert row is not None and row[0] == 0, "Test fixtures leaked into the test database."


@pytest.fixture
def ledger(database_target: DatabaseTarget) -> Iterator[FixtureLedger]:
    fixture_ledger = FixtureLedger(database_target)
    try:
        yield fixture_ledger
    finally:
        fixture_ledger.cleanup()


@pytest.fixture
def api_factory(database_target: DatabaseTarget) -> AsyncConnectionFactory:
    """Production connection factory (autocommit + SET ROLE lms_api) aimed at the test DB."""
    return create_connection_factory(SecretStr(database_target.api_url))
