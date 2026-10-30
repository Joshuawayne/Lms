"""PostgreSQL repository implementations for programs and applications using psycopg.

Implements ProgramRepository and ApplicationRepository targeting the private
'lms' schema with RLS and the 'lms_api' role.

Receipt isolation: every read or write of an application row happens inside a
transaction that first sets the transaction-local ``lms.request_key`` setting.
The database policy only exposes the row whose idempotency key equals it, and
PostgreSQL clears the setting when the transaction ends, so a reused connection
never carries one request's scope into another.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Generator
from contextlib import AbstractAsyncContextManager, contextmanager
from datetime import datetime
from typing import Any

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from app.modules.programs.application.errors import (
    ApplicationsClosedError,
    IdempotencyConflictError,
    ProgramServiceUnavailableError,
)
from app.modules.programs.application.ports import (
    ApplicationReplayRecord,
    ApplicationRepository,
    ApplicationSubmission,
    ProgramRepository,
    SubmissionResult,
)
from app.modules.programs.domain.entities import Program
from app.modules.programs.domain.values import (
    ApplicationStatus,
    Pathway,
    ProgramDelivery,
    ProgramStatus,
)

AsyncConnectionFactory = Callable[[], AbstractAsyncContextManager[psycopg.AsyncConnection[Any]]]

_PROGRAM_COLUMNS = (
    "id, pathway, title, slug, summary, description, delivery, status, "
    "applications_enabled, applications_open_at, applications_close_at, "
    "starts_on, ends_on, max_enrolments, min_age_years, max_age_years, "
    "display_order, created_at, updated_at"
)
_RECEIPT_COLUMNS = (
    "id, idempotency_key, request_fingerprint, program_id, status, submitted_at, reference"
)

# Transaction-local (is_local = true): PostgreSQL discards it at COMMIT/ROLLBACK.
_SCOPE_RECEIPTS_TO_KEY = "SELECT set_config('lms.request_key', %(key)s, true)"


@contextmanager
def _unavailable_as_service_error() -> Generator[None]:
    """Report connectivity failures as retryable service errors, never as 'not found'."""
    try:
        yield
    except (psycopg.OperationalError, OSError) as error:
        raise ProgramServiceUnavailableError() from error


async def _scope_to_request_key(cur: psycopg.AsyncCursor[Any], key: uuid.UUID) -> None:
    """Limit receipt visibility to one idempotency key for the current transaction only."""
    await cur.execute(_SCOPE_RECEIPTS_TO_KEY, {"key": str(key)})


def _row_to_program(row: dict[str, Any]) -> Program:
    return Program(
        id=row["id"],
        pathway=Pathway(row["pathway"]),
        title=row["title"],
        slug=row["slug"],
        summary=row["summary"],
        description=row["description"],
        delivery=ProgramDelivery(row["delivery"]),
        status=ProgramStatus(row["status"]),
        applications_enabled=row["applications_enabled"],
        applications_open_at=row["applications_open_at"],
        applications_close_at=row["applications_close_at"],
        starts_on=row["starts_on"],
        ends_on=row["ends_on"],
        max_enrolments=row["max_enrolments"],
        min_age_years=row["min_age_years"],
        max_age_years=row["max_age_years"],
        display_order=row["display_order"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_replay_record(row: dict[str, Any]) -> ApplicationReplayRecord:
    return ApplicationReplayRecord(
        id=row["id"],
        idempotency_key=row["idempotency_key"],
        request_fingerprint=row["request_fingerprint"],
        program_id=row["program_id"],
        status=ApplicationStatus(row["status"]),
        submitted_at=row["submitted_at"],
        reference=row["reference"],
    )


class PostgresProgramRepository(ProgramRepository):
    """PostgreSQL implementation of ProgramRepository."""

    def __init__(self, connection_factory: AsyncConnectionFactory) -> None:
        self._connection_factory = connection_factory

    async def list_published(
        self,
        *,
        pathway: Pathway | None = None,
        page: int = 1,
        page_size: int = 12,
    ) -> tuple[list[Program], int]:
        offset = (page - 1) * page_size
        params: dict[str, Any] = {"limit": page_size, "offset": offset}
        if pathway is not None:
            params["pathway"] = pathway.value
            pathway_filter = sql.SQL("AND pathway = %(pathway)s ")
        else:
            pathway_filter = sql.SQL("")

        count_query = sql.SQL(
            "SELECT count(*) AS total FROM lms.programs WHERE status = 'published' {}"
        ).format(pathway_filter)
        # display_order and created_at are not unique; the id tie-breaker keeps pages stable
        # so a program can never repeat on, or vanish between, adjacent pages.
        list_query = sql.SQL(
            f"SELECT {_PROGRAM_COLUMNS} FROM lms.programs "
            "WHERE status = 'published' {}"
            "ORDER BY display_order ASC, created_at ASC, id ASC "
            "LIMIT %(limit)s OFFSET %(offset)s"
        ).format(pathway_filter)
        with _unavailable_as_service_error():
            async with (
                self._connection_factory() as conn,
                conn.cursor(row_factory=dict_row) as cur,
            ):
                await cur.execute(count_query, params)
                count_row = await cur.fetchone()
                total = count_row["total"] if count_row else 0
                await cur.execute(list_query, params)
                rows = await cur.fetchall()
                return [_row_to_program(row) for row in rows], total

    async def get_published_by_id(self, program_id: uuid.UUID) -> Program | None:
        return await self._get_one(sql.SQL("id = %(value)s"), program_id)

    async def get_by_slug(self, slug: str) -> Program | None:
        return await self._get_one(sql.SQL("slug = %(value)s"), slug)

    async def _get_one(self, predicate: sql.SQL, value: object) -> Program | None:
        with _unavailable_as_service_error():
            async with (
                self._connection_factory() as conn,
                conn.cursor(row_factory=dict_row) as cur,
            ):
                query = sql.SQL(
                    f"SELECT {_PROGRAM_COLUMNS} FROM lms.programs "
                    "WHERE {} AND status = 'published'"
                ).format(predicate)
                await cur.execute(query, {"value": value})
                row = await cur.fetchone()
                return _row_to_program(row) if row else None


class PostgresApplicationRepository(ApplicationRepository):
    """PostgreSQL implementation of ApplicationRepository."""

    def __init__(self, connection_factory: AsyncConnectionFactory) -> None:
        self._connection_factory = connection_factory

    async def get_current_time(self) -> datetime:
        with _unavailable_as_service_error():
            async with (
                self._connection_factory() as conn,
                conn.cursor() as cur,
            ):
                await cur.execute("SELECT now()")
                row = await cur.fetchone()
                if row is None or not isinstance(row[0], datetime):
                    msg = "Unable to fetch current timestamp from database"
                    raise RuntimeError(msg)
                return row[0]

    async def find_by_idempotency_key(self, key: uuid.UUID) -> ApplicationReplayRecord | None:
        with _unavailable_as_service_error():
            async with (
                self._connection_factory() as conn,
                conn.transaction(),
                conn.cursor(row_factory=dict_row) as cur,
            ):
                await _scope_to_request_key(cur, key)
                return await self._select_receipt(cur, key)

    async def insert_application(self, submission: ApplicationSubmission) -> SubmissionResult:
        with _unavailable_as_service_error():
            # The transaction block commits (or rolls back) on exit, BEFORE the
            # outcome below is handed to the caller, so a confirmation is never
            # returned for rows that were not durably committed.
            async with (
                self._connection_factory() as conn,
                conn.transaction(),
                conn.cursor(row_factory=dict_row) as cur,
            ):
                outcome = await self._insert_in_transaction(cur, submission)
        return outcome

    async def _insert_in_transaction(
        self, cur: psycopg.AsyncCursor[dict[str, Any]], submission: ApplicationSubmission
    ) -> SubmissionResult:
        await _scope_to_request_key(cur, submission.idempotency_key)

        # Availability is enforced atomically in the conditional INSERT ... SELECT and
        # again by the insert RLS policy.  ON CONFLICT lets a concurrent replay fall
        # through to the receipt lookup below instead of raising.
        insert_query = (
            "INSERT INTO lms.enrolment_applications ("
            "idempotency_key, request_fingerprint, program_id, "
            "guardian_name, guardian_email, guardian_phone, guardian_relationship, "
            "learner_name, learner_age_years, notes, declaration_version, reference"
            ") "
            "SELECT "
            "%(idempotency_key)s, %(request_fingerprint)s, p.id, "
            "%(guardian_name)s, %(guardian_email)s, %(guardian_phone)s, "
            "%(guardian_relationship)s, %(learner_name)s, %(learner_age_years)s, "
            "%(notes)s, %(declaration_version)s, %(reference)s "
            "FROM lms.programs p "
            "WHERE p.id = %(program_id)s "
            "  AND p.status = 'published' "
            "  AND p.applications_enabled = true "
            "  AND (p.applications_open_at IS NULL OR now() >= p.applications_open_at) "
            "  AND (p.applications_close_at IS NULL OR now() < p.applications_close_at) "
            "ON CONFLICT (idempotency_key) DO NOTHING "
            f"RETURNING {_RECEIPT_COLUMNS}"
        )
        params = {
            "idempotency_key": submission.idempotency_key,
            "request_fingerprint": submission.request_fingerprint,
            "program_id": submission.program_id,
            "guardian_name": submission.guardian_name,
            "guardian_email": submission.guardian_email,
            "guardian_phone": submission.guardian_phone,
            "guardian_relationship": submission.guardian_relationship.value,
            "learner_name": submission.learner_name,
            "learner_age_years": submission.learner_age_years,
            "notes": submission.notes,
            "declaration_version": submission.declaration_version,
            "reference": submission.reference,
        }
        await cur.execute(insert_query, params)
        row = await cur.fetchone()

        if row is not None:
            record = _row_to_replay_record(row)
            await self._record_submitted_event(cur, record.id)
            return SubmissionResult(record=record, is_new=True)

        # Concurrency race or program not accepting applications: look for an existing row
        # with this idempotency key (visible because the transaction is scoped to it).
        existing_row = await self._select_receipt(cur, submission.idempotency_key)
        if existing_row is not None:
            if existing_row.request_fingerprint == submission.request_fingerprint:
                return SubmissionResult(record=existing_row, is_new=False)
            raise IdempotencyConflictError()

        raise ApplicationsClosedError(
            "this program", "it is not currently published or open for applications."
        )

    async def _record_submitted_event(
        self, cur: psycopg.AsyncCursor[dict[str, Any]], application_id: uuid.UUID
    ) -> None:
        """Write the 'submitted' audit event in the same transaction as the application row.

        Kept as its own method so a test can inject a controlled audit failure and
        prove that the application insert is rolled back with it.
        """
        await cur.execute(
            "INSERT INTO lms.application_audit_events ("
            "application_id, event_type, actor_id, detail"
            ") VALUES (%(application_id)s, 'submitted', NULL, NULL)",
            {"application_id": application_id},
        )

    @staticmethod
    async def _select_receipt(
        cur: psycopg.AsyncCursor[dict[str, Any]], key: uuid.UUID
    ) -> ApplicationReplayRecord | None:
        await cur.execute(
            f"SELECT {_RECEIPT_COLUMNS} FROM lms.enrolment_applications "
            "WHERE idempotency_key = %(key)s",
            {"key": key},
        )
        row = await cur.fetchone()
        return _row_to_replay_record(row) if row else None
