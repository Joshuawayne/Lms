"""Unit tests for domain entities and invariants in the programs module."""

from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest

from app.modules.programs.domain.entities import Program
from app.modules.programs.domain.values import (
    Pathway,
    ProgramDelivery,
    ProgramStatus,
)


def _make_program(
    *,
    status: ProgramStatus = ProgramStatus.PUBLISHED,
    applications_enabled: bool = True,
    applications_open_at: datetime | None = None,
    applications_close_at: datetime | None = None,
    min_age_years: int | None = 7,
    max_age_years: int | None = 14,
) -> Program:
    now = datetime.now(UTC)
    return Program(
        id=uuid4(),
        pathway=Pathway.SATURDAY_CLUB,
        title="Saturday Robotics",
        slug="saturday-robotics",
        summary="Hands-on robotics club",
        description="Detailed curriculum",
        delivery=ProgramDelivery.IN_PERSON,
        status=status,
        applications_enabled=applications_enabled,
        applications_open_at=applications_open_at,
        applications_close_at=applications_close_at,
        starts_on=date(2027, 1, 10),
        ends_on=date(2027, 4, 10),
        max_enrolments=20,
        min_age_years=min_age_years,
        max_age_years=max_age_years,
        display_order=1,
        created_at=now,
        updated_at=now,
    )


def test_program_accepts_applications_when_published_and_enabled() -> None:
    program = _make_program()
    assert program.accepts_applications(datetime.now(UTC)) is True


@pytest.mark.parametrize("status", [ProgramStatus.DRAFT, ProgramStatus.ARCHIVED])
def test_program_rejects_applications_when_not_published(status: ProgramStatus) -> None:
    program = _make_program(status=status)
    assert program.accepts_applications(datetime.now(UTC)) is False


def test_program_rejects_applications_when_applications_disabled() -> None:
    program = _make_program(applications_enabled=False)
    assert program.accepts_applications(datetime.now(UTC)) is False


def test_program_window_boundaries() -> None:
    now = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
    open_at = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)
    close_at = datetime(2026, 11, 15, 17, 0, tzinfo=UTC)

    program = _make_program(
        applications_open_at=open_at,
        applications_close_at=close_at,
    )

    # Before open
    assert program.accepts_applications(open_at - timedelta(seconds=1)) is False
    # Exactly at open
    assert program.accepts_applications(open_at) is True
    # Inside window
    assert program.accepts_applications(now) is True
    # Exactly at close (exclusive)
    assert program.accepts_applications(close_at) is False
    # After close
    assert program.accepts_applications(close_at + timedelta(seconds=1)) is False


def test_program_open_window_with_null_bounds() -> None:
    now = datetime.now(UTC)

    # Open from start of time until close_at
    prog1 = _make_program(applications_close_at=now + timedelta(days=1))
    assert prog1.accepts_applications(now) is True

    # Open from open_at indefinitely
    prog2 = _make_program(applications_open_at=now - timedelta(days=1))
    assert prog2.accepts_applications(now) is True
