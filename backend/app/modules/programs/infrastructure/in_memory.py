"""In-memory repository adapters for the programs module.

Useful for unit and integration testing without database dependencies.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.modules.programs.application.errors import (
    ApplicationsClosedError,
    IdempotencyConflictError,
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
    ProgramStatus,
)


class InMemoryProgramRepository(ProgramRepository):
    """In-memory program repository for fast deterministic testing."""

    def __init__(self, programs: list[Program] | None = None) -> None:
        self._programs: dict[uuid.UUID, Program] = {p.id: p for p in (programs or [])}

    def add(self, program: Program) -> None:
        self._programs[program.id] = program

    async def list_published(
        self,
        *,
        pathway: Pathway | None = None,
        page: int = 1,
        page_size: int = 12,
    ) -> tuple[list[Program], int]:
        matches = [
            p
            for p in self._programs.values()
            if p.status == ProgramStatus.PUBLISHED and (pathway is None or p.pathway == pathway)
        ]
        # Same ordering contract as PostgreSQL: display_order, created_at, then unique id.
        matches.sort(key=lambda p: (p.display_order, p.created_at, p.id))

        total = len(matches)
        start = (page - 1) * page_size
        end = start + page_size
        return matches[start:end], total

    async def get_published_by_id(self, program_id: uuid.UUID) -> Program | None:
        prog = self._programs.get(program_id)
        if prog is not None and prog.status == ProgramStatus.PUBLISHED:
            return prog
        return None

    async def get_by_slug(self, slug: str) -> Program | None:
        for p in self._programs.values():
            if p.slug == slug and p.status == ProgramStatus.PUBLISHED:
                return p
        return None


class InMemoryApplicationRepository(ApplicationRepository):
    """In-memory application repository with audit event tracking."""

    def __init__(
        self,
        fixed_now: datetime | None = None,
        program_repo: InMemoryProgramRepository | None = None,
    ) -> None:
        self._records_by_key: dict[uuid.UUID, ApplicationReplayRecord] = {}
        self._records_by_id: dict[uuid.UUID, ApplicationReplayRecord] = {}
        self._audit_events: list[dict[str, Any]] = []
        self._fixed_now = fixed_now
        self._program_repo = program_repo

    def set_current_time(self, now: datetime) -> None:
        self._fixed_now = now

    async def get_current_time(self) -> datetime:
        return self._fixed_now or datetime.now(UTC)

    async def find_by_idempotency_key(self, key: uuid.UUID) -> ApplicationReplayRecord | None:
        return self._records_by_key.get(key)

    async def insert_application(self, submission: ApplicationSubmission) -> SubmissionResult:
        if submission.idempotency_key in self._records_by_key:
            existing = self._records_by_key[submission.idempotency_key]
            if existing.request_fingerprint == submission.request_fingerprint:
                return SubmissionResult(record=existing, is_new=False)
            raise IdempotencyConflictError()

        now = await self.get_current_time()

        if self._program_repo is not None:
            prog = await self._program_repo.get_published_by_id(submission.program_id)
            if prog is None or not prog.accepts_applications(now):
                raise ApplicationsClosedError(prog.title if prog else "Program")

        app_id = uuid.uuid4()
        record = ApplicationReplayRecord(
            id=app_id,
            idempotency_key=submission.idempotency_key,
            request_fingerprint=submission.request_fingerprint,
            program_id=submission.program_id,
            status=ApplicationStatus.SUBMITTED,
            submitted_at=now,
            reference=submission.reference,
        )
        self._records_by_key[submission.idempotency_key] = record
        self._records_by_id[app_id] = record
        self._audit_events.append(
            {
                "id": uuid.uuid4(),
                "application_id": app_id,
                "event_type": "submitted",
                "actor_id": None,
                "detail": None,
                "occurred_at": now,
            }
        )
        return SubmissionResult(record=record, is_new=True)
