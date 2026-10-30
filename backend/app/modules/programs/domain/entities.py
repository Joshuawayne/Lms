"""Domain entities for the programs module.

Entities represent the core business objects.  They carry identity (a UUID)
and encapsulate invariants.  They do not depend on HTTP or database libraries.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime

from app.modules.programs.domain.values import (
    ApplicationStatus,
    GuardianRelationship,
    Pathway,
    ProgramDelivery,
    ProgramStatus,
)


@dataclass(frozen=True)
class Program:
    """A published or draft learning program in the catalogue.

    The public listing shows only programs with status == PUBLISHED.
    Application availability depends on status, applications_enabled,
    and the open/close window evaluated against the current database time.
    """

    id: uuid.UUID
    pathway: Pathway
    title: str
    slug: str
    summary: str
    description: str
    delivery: ProgramDelivery
    status: ProgramStatus
    applications_enabled: bool
    applications_open_at: datetime | None
    applications_close_at: datetime | None
    starts_on: date | None
    ends_on: date | None
    max_enrolments: int | None
    min_age_years: int | None
    max_age_years: int | None
    display_order: int
    created_at: datetime
    updated_at: datetime

    def accepts_applications(self, now: datetime) -> bool:
        """Whether this program currently accepts new applications.

        A program accepts applications when ALL of:
          - status is PUBLISHED
          - applications_enabled is True
          - now >= applications_open_at  (null open = no earliest boundary)
          - now <  applications_close_at (null close = no latest boundary)
        """
        if self.status != ProgramStatus.PUBLISHED:
            return False
        if not self.applications_enabled:
            return False
        if self.applications_open_at is not None and now < self.applications_open_at:
            return False
        return not (self.applications_close_at is not None and now >= self.applications_close_at)


@dataclass(frozen=True)
class EnrolmentApplication:
    """An unverified application submitted by a guardian.

    Applications are intentionally separate from approved enrolments.
    They do not create learner identities, guardian relationships or
    accounts.  Those are established through the later approval workflow.
    """

    id: uuid.UUID
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
    declaration_accepted_at: datetime
    declaration_version: int
    status: ApplicationStatus
    submitted_at: datetime
    reviewed_at: datetime | None
    reference: str
