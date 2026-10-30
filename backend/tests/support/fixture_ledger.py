"""Committed database fixtures that are always removed afterwards."""

from __future__ import annotations

import uuid
from typing import Any

import psycopg
from psycopg.rows import dict_row

from .database_target import DatabaseTarget

FIXTURE_SLUG_PREFIX = "it-"

# Availability states for program fixtures.  Values are fixed SQL fragments (never user
# input), so interpolating them below cannot inject anything.
_PROGRAM_STATES: dict[str, dict[str, str]] = {
    "open": {
        "status": "published",
        "enabled": "true",
        "opens": "now() - interval '1 hour'",
        "closes": "now() + interval '10 days'",
    },
    "draft": {
        "status": "draft",
        "enabled": "true",
        "opens": "now() - interval '1 day'",
        "closes": "now() + interval '10 days'",
    },
    "disabled": {
        "status": "published",
        "enabled": "false",
        "opens": "now() - interval '1 day'",
        "closes": "now() + interval '10 days'",
    },
    "future": {
        "status": "published",
        "enabled": "true",
        "opens": "now() + interval '5 days'",
        "closes": "now() + interval '20 days'",
    },
    "expired": {
        "status": "published",
        "enabled": "true",
        "opens": "now() - interval '20 days'",
        "closes": "now() - interval '1 day'",
    },
}


class FixtureLedger:
    """Create committed fixtures through the maintenance role and delete them afterwards.

    Everything created here is registered, so ``cleanup`` removes exactly those rows (audit
    events, applications, programs) even when the test failed half-way.
    """

    def __init__(self, target: DatabaseTarget) -> None:
        self._url = target.maintenance_url_for(target.database)
        self._run = uuid.uuid4().hex[:8]
        self._program_ids: list[uuid.UUID] = []

    def connect(self) -> psycopg.Connection[dict[str, Any]]:
        return psycopg.connect(self._url, autocommit=True, row_factory=dict_row)

    def create_program(self, purpose: str, state: str = "open") -> uuid.UUID:
        spec = _PROGRAM_STATES[state]
        slug = f"{FIXTURE_SLUG_PREFIX}{self._run}-{purpose}-{state}"
        with self.connect() as conn:
            row = conn.execute(
                f"""
                INSERT INTO lms.programs (
                    pathway, title, slug, summary, description, delivery, status,
                    applications_enabled, applications_open_at, applications_close_at,
                    starts_on, ends_on, min_age_years, max_age_years, display_order
                ) VALUES (
                    'saturday_club', %(title)s, %(slug)s, 'Fixture', 'Fixture program',
                    'in_person', '{spec["status"]}', {spec["enabled"]},
                    {spec["opens"]}, {spec["closes"]},
                    '2027-01-01', '2027-04-01', 7, 17, 1
                ) RETURNING id
                """,  # type: ignore[arg-type]
                {"title": f"Fixture {purpose} {state}", "slug": slug},
            ).fetchone()
        assert row is not None
        program_id: uuid.UUID = row["id"]
        self._program_ids.append(program_id)
        return program_id

    def create_application(self, program_id: uuid.UUID, *, reference: str) -> uuid.UUID:
        """Insert an application plus its audit event directly (bypassing the API role)."""
        with self.connect() as conn:
            row = conn.execute(
                """
                INSERT INTO lms.enrolment_applications (
                    idempotency_key, request_fingerprint, program_id, guardian_name,
                    guardian_email, guardian_relationship, learner_name, learner_age_years,
                    declaration_version, reference
                ) VALUES (%s, %s, %s, 'Fixture Guardian', 'fixture@example.test', 'parent',
                          'Fixture Learner', 10, 1, %s)
                RETURNING id
                """,
                (uuid.uuid4(), "c" * 64, program_id, reference),
            ).fetchone()
            assert row is not None
            application_id: uuid.UUID = row["id"]
            conn.execute(
                "INSERT INTO lms.application_audit_events (application_id, event_type) "
                "VALUES (%s, 'submitted')",
                (application_id,),
            )
        return application_id

    def close_applications(self, program_id: uuid.UUID) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE lms.programs SET applications_enabled = false, "
                "applications_close_at = now() - interval '1 hour' WHERE id = %s",
                (program_id,),
            )

    def scalar(self, query: str, params: tuple[object, ...] = ()) -> Any:
        """Run an independent maintenance query and return its single value."""
        with self.connect() as conn:
            row = conn.execute(query, params).fetchone()  # type: ignore[call-overload]
        assert row is not None
        return next(iter(row.values()))

    def cleanup(self) -> None:
        if not self._program_ids:
            return
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM lms.application_audit_events WHERE application_id IN "
                "(SELECT id FROM lms.enrolment_applications WHERE program_id = ANY(%s))",
                (self._program_ids,),
            )
            conn.execute(
                "DELETE FROM lms.enrolment_applications WHERE program_id = ANY(%s)",
                (self._program_ids,),
            )
            conn.execute("DELETE FROM lms.programs WHERE id = ANY(%s)", (self._program_ids,))
        self._program_ids.clear()
