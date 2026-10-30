"""Native PostgreSQL tests for application receipts, RLS, atomicity and concurrency.

Evidence class: NATIVE DATABASE.  These run against the isolated ``lms_test`` database
(see conftest.py) through independent connections.  Fixtures are committed for real,
then removed in failure-safe teardown.  Mocks and in-memory repositories are not used.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import psycopg
import pytest
from psycopg.errors import InsufficientPrivilege
from psycopg.rows import dict_row
from support.fixture_ledger import FixtureLedger

from app.infrastructure.database.connection import AsyncConnectionFactory
from app.modules.programs.application.commands import compute_payload_fingerprint
from app.modules.programs.application.errors import (
    ApplicationsClosedError,
    IdempotencyConflictError,
)
from app.modules.programs.application.ports import ApplicationSubmission
from app.modules.programs.domain.values import GuardianRelationship
from app.modules.programs.infrastructure.postgres import PostgresApplicationRepository

# Authorization failures must be exactly "insufficient_privilege"; any other database
# error (for example an invalid enum value) would mean the test proved nothing.
INSUFFICIENT_PRIVILEGE = "42501"


def _submission(
    program_id: uuid.UUID,
    *,
    key: uuid.UUID | None = None,
    learner_name: str = "Test Learner",
    notes: str | None = "Testing integration",
) -> ApplicationSubmission:
    key = key or uuid.uuid4()
    fingerprint = compute_payload_fingerprint(
        program_id=program_id,
        guardian_name="Test Guardian",
        guardian_email="guardian@example.test",
        guardian_phone="+254700000000",
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name=learner_name,
        learner_age_years=10,
        notes=notes,
        declaration_version=1,
    )
    return ApplicationSubmission(
        idempotency_key=key,
        request_fingerprint=fingerprint,
        program_id=program_id,
        guardian_name="Test Guardian",
        guardian_email="guardian@example.test",
        guardian_phone="+254700000000",
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name=learner_name,
        learner_age_years=10,
        notes=notes,
        declaration_version=1,
        reference=f"APP-TEST-{str(key)[:8].upper()}",
    )


async def _scoped_references(conn: psycopg.AsyncConnection[Any], key: object | None) -> list[str]:
    """Read receipt references as lms_api, inside a transaction scoped to ``key``."""
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        if key is not None:
            await cur.execute("SELECT set_config('lms.request_key', %s, true)", (str(key),))
        await cur.execute("SELECT reference FROM lms.enrolment_applications ORDER BY reference")
        return [row["reference"] for row in await cur.fetchall()]


async def _expect_privilege_error(
    conn: psycopg.AsyncConnection[Any], statement: str, params: tuple[object, ...] = ()
) -> str:
    """Run ``statement`` as lms_api and return the denial message, asserting SQLSTATE 42501."""
    with pytest.raises(InsufficientPrivilege) as caught:
        await conn.execute(statement, params)  # type: ignore[arg-type]
    assert caught.value.sqlstate == INSUFFICIENT_PRIVILEGE
    return str(caught.value)


# ─── receipt isolation (request-key scope) ─────────────────────────────────────────────


@pytest.mark.anyio
async def test_receipts_are_invisible_without_a_request_scope(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    """Missing scope fails closed: two real receipts exist yet lms_api sees none."""
    program_id = ledger.create_program("scope-none")
    ledger.create_application(program_id, reference="APP-TEST-SCOPE-A1")
    ledger.create_application(program_id, reference="APP-TEST-SCOPE-A2")

    async with api_factory() as conn:
        assert await _scoped_references(conn, None) == []


@pytest.mark.anyio
async def test_wrong_and_malformed_scopes_see_nothing_and_the_right_scope_sees_one(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("scope-key")
    repo = PostgresApplicationRepository(api_factory)
    key_a, key_b = uuid.uuid4(), uuid.uuid4()
    await repo.insert_application(_submission(program_id, key=key_a))
    await repo.insert_application(_submission(program_id, key=key_b))

    async with api_factory() as conn:
        assert await _scoped_references(conn, uuid.uuid4()) == []
        assert await _scoped_references(conn, "not-a-uuid") == []
        assert await _scoped_references(conn, "") == []
        assert await _scoped_references(conn, key_a) == [f"APP-TEST-{str(key_a)[:8].upper()}"]
        assert await _scoped_references(conn, key_b) == [f"APP-TEST-{str(key_b)[:8].upper()}"]


@pytest.mark.anyio
async def test_scope_is_cleared_when_the_transaction_ends_on_a_reused_connection(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("scope-reuse")
    repo = PostgresApplicationRepository(api_factory)
    key = uuid.uuid4()
    await repo.insert_application(_submission(program_id, key=key))

    async with api_factory() as conn:
        assert len(await _scoped_references(conn, key)) == 1
        # Same connection, new transaction, no scope: nothing may leak from the previous one.
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT reference FROM lms.enrolment_applications")
            assert await cur.fetchall() == []
            await cur.execute("SELECT nullif(current_setting('lms.request_key', true), '') AS s")
            leftover = await cur.fetchone()
            assert leftover is not None
            assert leftover["s"] is None


@pytest.mark.anyio
async def test_personal_columns_stay_denied_even_with_the_correct_scope(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("personal")
    repo = PostgresApplicationRepository(api_factory)
    key = uuid.uuid4()
    await repo.insert_application(_submission(program_id, key=key))

    async with api_factory() as conn:
        columns = (
            "guardian_email",
            "guardian_name",
            "guardian_phone",
            "learner_name",
            "notes",
        )
        for column in columns:
            async with conn.transaction():
                await conn.execute("SELECT set_config('lms.request_key', %s, true)", (str(key),))
                with pytest.raises(InsufficientPrivilege) as caught:
                    await conn.execute(
                        f"SELECT {column} FROM lms.enrolment_applications"  # type: ignore[arg-type]
                    )
            assert caught.value.sqlstate == INSUFFICIENT_PRIVILEGE


# ─── denied mutations and privileged values ────────────────────────────────────────────


@pytest.mark.anyio
async def test_runtime_role_cannot_update_or_delete_applications_or_audit_events(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("mutations")
    ledger.create_application(program_id, reference="APP-TEST-MUTATE")

    async with api_factory() as conn:
        for statement in (
            "UPDATE lms.enrolment_applications SET status = 'approved'",
            "DELETE FROM lms.enrolment_applications",
            "UPDATE lms.application_audit_events SET detail = '{}'::jsonb",
            "DELETE FROM lms.application_audit_events",
        ):
            await _expect_privilege_error(conn, statement)

    assert (
        ledger.scalar(
            "SELECT status::text FROM lms.enrolment_applications WHERE reference = %s",
            ("APP-TEST-MUTATE",),
        )
        == "submitted"
    )


@pytest.mark.anyio
async def test_runtime_role_cannot_insert_a_reviewed_status_or_reviewer_timestamp(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("privileged-values")
    base = (
        "INSERT INTO lms.enrolment_applications (idempotency_key, request_fingerprint, "
        "program_id, guardian_name, guardian_email, guardian_relationship, learner_name, "
        "learner_age_years, declaration_version, reference, {extra}) "
        "VALUES (%s, %s, %s, 'G', 'g@example.test', 'parent', 'L', 10, 1, %s, {value})"
    )
    async with api_factory() as conn:
        for extra, value in (("status", "'approved'"), ("reviewed_at", "now()")):
            statement = base.format(extra=extra, value=value)
            await _expect_privilege_error(
                conn, statement, (uuid.uuid4(), "a" * 64, program_id, f"APP-TEST-{extra}")
            )
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.enrolment_applications WHERE program_id = %s", (program_id,)
        )
        == 0
    )


@pytest.mark.anyio
async def test_audit_policy_rejects_review_events_and_actor_ids_for_a_real_application(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    """Valid enum values and a real application, so only the RLS policy can say no."""
    program_id = ledger.create_program("audit-policy")
    application_id = ledger.create_application(program_id, reference="APP-TEST-AUDIT")

    async with api_factory() as conn:
        message = await _expect_privilege_error(
            conn,
            "INSERT INTO lms.application_audit_events (application_id, event_type) "
            "VALUES (%s, 'reviewed')",
            (application_id,),
        )
        assert "row-level security" in message
        message = await _expect_privilege_error(
            conn,
            "INSERT INTO lms.application_audit_events (application_id, event_type, actor_id) "
            "VALUES (%s, 'submitted', %s)",
            (application_id, uuid.uuid4()),
        )
        assert "row-level security" in message

    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.application_audit_events WHERE application_id = %s",
            (application_id,),
        )
        == 1
    )  # only the fixture's own submitted event


# ─── program availability enforced by the database itself ──────────────────────────────


@pytest.mark.anyio
@pytest.mark.parametrize("state", ["draft", "disabled", "future", "expired"])
async def test_database_policy_rejects_a_direct_insert_for_an_unavailable_program(
    state: str, ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    """Bypass the repository's filtered INSERT...SELECT: the policy alone must refuse."""
    program_id = ledger.create_program("rls", state)
    async with api_factory() as conn:
        message = await _expect_privilege_error(
            conn,
            "INSERT INTO lms.enrolment_applications (idempotency_key, request_fingerprint, "
            "program_id, guardian_name, guardian_email, guardian_relationship, learner_name, "
            "learner_age_years, declaration_version, reference) "
            "VALUES (%s, %s, %s, 'G', 'g@example.test', 'parent', 'L', 10, 1, %s)",
            (uuid.uuid4(), "a" * 64, program_id, f"APP-TEST-RLS-{state}"),
        )
    assert "row-level security" in message
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.enrolment_applications WHERE program_id = %s", (program_id,)
        )
        == 0
    )


@pytest.mark.anyio
@pytest.mark.parametrize("state", ["draft", "disabled", "future", "expired"])
async def test_repository_reports_closed_and_persists_nothing_for_unavailable_programs(
    state: str, ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("repo-closed", state)
    repo = PostgresApplicationRepository(api_factory)
    closed_submission = _submission(program_id)
    with pytest.raises(ApplicationsClosedError):
        await repo.insert_application(closed_submission)
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.enrolment_applications WHERE program_id = %s", (program_id,)
        )
        == 0
    )


# ─── commit, replay, conflict, closure ─────────────────────────────────────────────────


@pytest.mark.anyio
async def test_new_submission_is_committed_with_exactly_one_audit_event(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("commit")
    repo = PostgresApplicationRepository(api_factory)
    submission = _submission(program_id)

    result = await repo.insert_application(submission)
    assert result.is_new is True

    # Independent connection: the confirmation we received is backed by committed rows.
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.enrolment_applications WHERE idempotency_key = %s",
            (submission.idempotency_key,),
        )
        == 1
    )
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.application_audit_events WHERE application_id = %s",
            (result.record.id,),
        )
        == 1
    )

    replay = await repo.insert_application(submission)
    assert replay.is_new is False
    assert replay.record.id == result.record.id
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.application_audit_events WHERE application_id = %s",
            (result.record.id,),
        )
        == 1
    )


@pytest.mark.anyio
async def test_matching_and_conflicting_retries(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("retry")
    repo = PostgresApplicationRepository(api_factory)
    key = uuid.uuid4()
    first = await repo.insert_application(_submission(program_id, key=key))

    second = await repo.insert_application(_submission(program_id, key=key))
    assert second.is_new is False
    assert second.record.reference == first.record.reference

    conflicting_submission = _submission(
        program_id, key=key, learner_name="Other Name", notes="different notes"
    )
    with pytest.raises(IdempotencyConflictError):
        await repo.insert_application(conflicting_submission)
    assert await repo.find_by_idempotency_key(key) is not None
    assert await repo.find_by_idempotency_key(uuid.uuid4()) is None


@pytest.mark.anyio
async def test_replay_and_lookup_still_work_after_the_program_closes(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("closure")
    repo = PostgresApplicationRepository(api_factory)
    key = uuid.uuid4()
    submission = _submission(program_id, key=key)
    first = await repo.insert_application(submission)

    ledger.close_applications(program_id)

    replay = await repo.insert_application(submission)
    assert replay.is_new is False
    assert replay.record.id == first.record.id
    found = await repo.find_by_idempotency_key(key)
    assert found is not None
    assert found.reference == first.record.reference

    altered_submission = _submission(program_id, key=key, notes="altered after close")
    with pytest.raises(IdempotencyConflictError):
        await repo.insert_application(altered_submission)
    closed_submission = _submission(program_id)
    with pytest.raises(ApplicationsClosedError):
        await repo.insert_application(closed_submission)


@pytest.mark.anyio
async def test_concurrent_submissions_create_one_application_and_one_audit_event(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("concurrent")
    submission = _submission(program_id)
    # Two repositories, two independent connections, the same idempotency key.
    results = await asyncio.gather(
        PostgresApplicationRepository(api_factory).insert_application(submission),
        PostgresApplicationRepository(api_factory).insert_application(submission),
    )

    assert sorted(result.is_new for result in results) == [False, True]
    assert results[0].record.id == results[1].record.id
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.enrolment_applications WHERE idempotency_key = %s",
            (submission.idempotency_key,),
        )
        == 1
    )
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.application_audit_events WHERE application_id = %s",
            (results[0].record.id,),
        )
        == 1
    )


# ─── rollback through the production repository ────────────────────────────────────────


class _AuditFailingRepository(PostgresApplicationRepository):
    """Production repository with a controlled failure at the audit step only.

    The real audit INSERT is attempted with a forbidden actor_id, so PostgreSQL itself
    rejects it (SQLSTATE 42501).  Before that, the hook records whether the application row
    was already visible inside the transaction, proving the failure happened AFTER the
    application insert rather than instead of it.
    """

    def __init__(self, factory: AsyncConnectionFactory) -> None:
        super().__init__(factory)
        self.application_id: uuid.UUID | None = None
        self.application_visible_before_failure: bool | None = None

    async def _record_submitted_event(
        self, cur: psycopg.AsyncCursor[dict[str, Any]], application_id: uuid.UUID
    ) -> None:
        self.application_id = application_id
        await cur.execute(
            "SELECT count(*) AS n FROM lms.enrolment_applications WHERE id = %s",
            (application_id,),
        )
        row = await cur.fetchone()
        self.application_visible_before_failure = row is not None and row["n"] == 1
        await cur.execute(
            "INSERT INTO lms.application_audit_events (application_id, event_type, actor_id) "
            "VALUES (%s, 'submitted', %s)",
            (application_id, uuid.uuid4()),
        )


@pytest.mark.anyio
async def test_audit_failure_rolls_back_the_application_through_the_production_repository(
    ledger: FixtureLedger, api_factory: AsyncConnectionFactory
) -> None:
    program_id = ledger.create_program("rollback")
    repo = _AuditFailingRepository(api_factory)
    submission = _submission(program_id)

    with pytest.raises(InsufficientPrivilege) as caught:
        await repo.insert_application(submission)

    assert caught.value.sqlstate == INSUFFICIENT_PRIVILEGE  # the audit step failed...
    assert repo.application_visible_before_failure is True  # ...after the insert succeeded
    assert repo.application_id is not None
    # Independent connection: neither record committed.
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.enrolment_applications WHERE idempotency_key = %s",
            (submission.idempotency_key,),
        )
        == 0
    )
    assert (
        ledger.scalar(
            "SELECT count(*) FROM lms.application_audit_events WHERE application_id = %s",
            (repo.application_id,),
        )
        == 0
    )
