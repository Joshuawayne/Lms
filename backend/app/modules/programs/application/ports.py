"""Repository contracts (ports) for the programs module.

These protocols define the capabilities that use cases need from
persistence. Concrete implementations live in the infrastructure layer
and are injected at the composition root.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.modules.programs.domain.entities import Program
from app.modules.programs.domain.values import (
    ApplicationStatus,
    GuardianRelationship,
    Pathway,
)


@dataclass(frozen=True)
class ApplicationReplayRecord:
    """Minimal non-personal application record for idempotency lookups and receipts.

    Keeps personal contact and learner details outside replay query scopes.
    """

    id: uuid.UUID
    idempotency_key: uuid.UUID
    request_fingerprint: str
    program_id: uuid.UUID
    status: ApplicationStatus
    submitted_at: datetime
    reference: str


@dataclass(frozen=True)
class ApplicationSubmission:
    """Immutable input payload for persisting a new enrolment application."""

    idempotency_key: uuid.UUID
    request_fingerprint: str
    program_id: uuid.UUID
    guardian_name: str
    guardian_email: str
    guardian_phone: str | None
    guardian_relationship: GuardianRelationship
    learner_name: str
    learner_age_years: int
    notes: str | None
    declaration_version: int
    reference: str


@dataclass(frozen=True)
class SubmissionResult:
    """Explicit outcome of an application insertion or idempotent replay."""

    record: ApplicationReplayRecord
    is_new: bool


class ProgramRepository(Protocol):
    """Read-only access to the published program catalogue."""

    async def list_published(
        self,
        *,
        pathway: Pathway | None = None,
        page: int = 1,
        page_size: int = 12,
    ) -> tuple[list[Program], int]:
        """Return published programs with optional pathway filter.

        Returns a tuple of (programs, total_count) for pagination.
        Programs are ordered by display_order then created_at.
        """
        ...

    async def get_published_by_id(self, program_id: uuid.UUID) -> Program | None:
        """Return a single published program by ID.

        Returns None for draft, archived or nonexistent programs, aligning
        directly with database RLS policies for the API role.
        """
        ...

    async def get_by_slug(self, slug: str) -> Program | None:
        """Return a published program by its URL slug.

        Returns None if draft, archived or nonexistent.
        """
        ...


class ApplicationRepository(Protocol):
    """Persistence for enrolment applications and their audit events.

    The insert_application method must create both the application row
    and its 'submitted' audit event in a single atomic transaction.
    """

    async def find_by_idempotency_key(self, key: uuid.UUID) -> ApplicationReplayRecord | None:
        """Look up an existing application by its client-supplied idempotency key.

        Returns the minimal replay record without personal contact details.
        """
        ...

    async def insert_application(self, submission: ApplicationSubmission) -> SubmissionResult:
        """Insert a new application and its 'submitted' audit event atomically.

        Enforces program availability within the database operation.
        If a concurrent insert with the same idempotency_key races this call:
          - Returns the winning record with is_new=False if request_fingerprint matches.
          - Raises IdempotencyConflictError if the request_fingerprint differs.
        Audit events are recorded only for newly inserted applications.
        """
        ...

    async def get_current_time(self) -> datetime:
        """Return the current database timestamp.

        Used for preliminary availability validation against database time.
        """
        ...
