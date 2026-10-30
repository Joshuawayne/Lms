"""Unit tests for query and command use cases in the programs module."""

import asyncio
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest

from app.modules.programs.application.commands import (
    SubmitApplicationCommand,
    SubmitApplicationUseCase,
)
from app.modules.programs.application.errors import (
    ApplicationsClosedError,
    DeclarationRequiredError,
    IdempotencyConflictError,
    LearnerIneligibleError,
    ProgramNotFoundError,
)
from app.modules.programs.application.queries import (
    GetPublishedProgramUseCase,
    ListPublishedProgramsQuery,
    ListPublishedProgramsUseCase,
)
from app.modules.programs.domain.entities import Program
from app.modules.programs.domain.values import (
    GuardianRelationship,
    Pathway,
    ProgramDelivery,
    ProgramStatus,
)
from app.modules.programs.infrastructure.in_memory import (
    InMemoryApplicationRepository,
    InMemoryProgramRepository,
)


def _sample_program(
    slug: str = "holiday-coding",
    pathway: Pathway = Pathway.HOLIDAY,
    status: ProgramStatus = ProgramStatus.PUBLISHED,
    applications_enabled: bool = True,
    min_age_years: int | None = 8,
    max_age_years: int | None = 16,
) -> Program:
    now = datetime.now(UTC)
    return Program(
        id=uuid4(),
        pathway=pathway,
        title=f"Program {slug}",
        slug=slug,
        summary="Fun holiday coding camp",
        description="Learn Python and game development",
        delivery=ProgramDelivery.HYBRID,
        status=status,
        applications_enabled=applications_enabled,
        applications_open_at=now - timedelta(days=5),
        applications_close_at=now + timedelta(days=30),
        starts_on=date(2027, 4, 1),
        ends_on=date(2027, 4, 15),
        max_enrolments=25,
        min_age_years=min_age_years,
        max_age_years=max_age_years,
        display_order=0,
        created_at=now,
        updated_at=now,
    )


def test_list_published_programs_filters_and_paginates() -> None:
    p1 = _sample_program("prog-1", pathway=Pathway.HOLIDAY)
    p2 = _sample_program("prog-2", pathway=Pathway.SATURDAY_CLUB)
    p3 = _sample_program("prog-3", pathway=Pathway.HOLIDAY, status=ProgramStatus.DRAFT)

    repo = InMemoryProgramRepository([p1, p2, p3])
    use_case = ListPublishedProgramsUseCase(repo)

    # All published
    result = asyncio.run(use_case.execute(ListPublishedProgramsQuery()))
    assert result.total == 2
    assert len(result.items) == 2

    # Filtered by pathway
    result_holiday = asyncio.run(
        use_case.execute(ListPublishedProgramsQuery(pathway=Pathway.HOLIDAY))
    )
    assert result_holiday.total == 1
    assert result_holiday.items[0].slug == "prog-1"


def test_get_published_program_finds_by_slug() -> None:
    prog = _sample_program("coding-camp")
    repo = InMemoryProgramRepository([prog])
    use_case = GetPublishedProgramUseCase(repo)

    found = asyncio.run(use_case.execute("coding-camp"))
    assert found.id == prog.id

    coro = use_case.execute("nonexistent")
    with pytest.raises(ProgramNotFoundError):
        asyncio.run(coro)


def test_get_published_by_id_respects_published_status() -> None:
    pub = _sample_program("pub", status=ProgramStatus.PUBLISHED)
    draft = _sample_program("draft", status=ProgramStatus.DRAFT)

    repo = InMemoryProgramRepository([pub, draft])
    assert asyncio.run(repo.get_published_by_id(pub.id)) is not None
    assert asyncio.run(repo.get_published_by_id(draft.id)) is None


def test_submit_application_happy_path() -> None:
    prog = _sample_program("holiday-robotics")
    prog_repo = InMemoryProgramRepository([prog])
    app_repo = InMemoryApplicationRepository(program_repo=prog_repo)

    use_case = SubmitApplicationUseCase(prog_repo, app_repo)
    idempotency_key = uuid4()

    cmd = SubmitApplicationCommand(
        idempotency_key=idempotency_key,
        program_slug="holiday-robotics",
        guardian_name="Grace Hopper",
        guardian_email="grace@example.com",
        guardian_phone="+254712345678",
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name="Ada Lovelace",
        learner_age_years=12,
        notes="Excited for robotics",
        declaration_accepted=True,
    )

    result = asyncio.run(use_case.execute(cmd))
    assert result.is_retry is False
    assert result.record.reference.startswith("JC-")
    assert len(app_repo._audit_events) == 1
    assert app_repo._audit_events[0]["event_type"] == "submitted"


def test_submit_application_idempotent_replay() -> None:
    prog = _sample_program("holiday-robotics")
    prog_repo = InMemoryProgramRepository([prog])
    app_repo = InMemoryApplicationRepository(program_repo=prog_repo)

    use_case = SubmitApplicationUseCase(prog_repo, app_repo)
    idempotency_key = uuid4()

    cmd = SubmitApplicationCommand(
        idempotency_key=idempotency_key,
        program_slug="holiday-robotics",
        guardian_name="Grace Hopper",
        guardian_email="grace@example.com",
        guardian_phone="+254712345678",
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name="Ada Lovelace",
        learner_age_years=12,
        notes=None,
        declaration_accepted=True,
    )

    first = asyncio.run(use_case.execute(cmd))
    assert first.is_retry is False

    # Second submission with exact same key and details
    second = asyncio.run(use_case.execute(cmd))
    assert second.is_retry is True
    assert second.record.id == first.record.id
    assert second.record.reference == first.record.reference
    # Audit events count remains 1 (no duplicate audit created on replay)
    assert len(app_repo._audit_events) == 1


def test_submit_application_idempotency_conflict() -> None:
    prog = _sample_program("holiday-robotics")
    prog_repo = InMemoryProgramRepository([prog])
    app_repo = InMemoryApplicationRepository(program_repo=prog_repo)

    use_case = SubmitApplicationUseCase(prog_repo, app_repo)
    idempotency_key = uuid4()

    cmd1 = SubmitApplicationCommand(
        idempotency_key=idempotency_key,
        program_slug="holiday-robotics",
        guardian_name="Grace Hopper",
        guardian_email="grace@example.com",
        guardian_phone=None,
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name="Ada Lovelace",
        learner_age_years=12,
        notes=None,
        declaration_accepted=True,
    )
    asyncio.run(use_case.execute(cmd1))

    # Reusing same key with a different learner name
    cmd2 = SubmitApplicationCommand(
        idempotency_key=idempotency_key,
        program_slug="holiday-robotics",
        guardian_name="Grace Hopper",
        guardian_email="grace@example.com",
        guardian_phone=None,
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name="Charles Babbage",
        learner_age_years=13,
        notes=None,
        declaration_accepted=True,
    )

    coro = use_case.execute(cmd2)
    with pytest.raises(IdempotencyConflictError):
        asyncio.run(coro)


def test_submit_application_replay_succeeds_even_when_applications_closed() -> None:
    prog = _sample_program("holiday-robotics")
    prog_repo = InMemoryProgramRepository([prog])
    app_repo = InMemoryApplicationRepository(program_repo=prog_repo)

    use_case = SubmitApplicationUseCase(prog_repo, app_repo)
    idempotency_key = uuid4()

    cmd = SubmitApplicationCommand(
        idempotency_key=idempotency_key,
        program_slug="holiday-robotics",
        guardian_name="Grace Hopper",
        guardian_email="grace@example.com",
        guardian_phone=None,
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name="Ada Lovelace",
        learner_age_years=12,
        notes=None,
        declaration_accepted=True,
    )

    first = asyncio.run(use_case.execute(cmd))
    assert first.is_retry is False

    # Applications for this program now close
    closed_prog = Program(
        id=prog.id,
        pathway=prog.pathway,
        title=prog.title,
        slug=prog.slug,
        summary=prog.summary,
        description=prog.description,
        delivery=prog.delivery,
        status=prog.status,
        applications_enabled=False,  # closed!
        applications_open_at=prog.applications_open_at,
        applications_close_at=prog.applications_close_at,
        starts_on=prog.starts_on,
        ends_on=prog.ends_on,
        max_enrolments=prog.max_enrolments,
        min_age_years=prog.min_age_years,
        max_age_years=prog.max_age_years,
        display_order=prog.display_order,
        created_at=prog.created_at,
        updated_at=datetime.now(UTC),
    )
    prog_repo.add(closed_prog)

    # Replay must still return the original receipt
    second = asyncio.run(use_case.execute(cmd))
    assert second.is_retry is True
    assert second.record.id == first.record.id


def test_submit_application_declaration_required() -> None:
    prog = _sample_program("open-prog")
    prog_repo = InMemoryProgramRepository([prog])
    app_repo = InMemoryApplicationRepository(program_repo=prog_repo)
    use_case = SubmitApplicationUseCase(prog_repo, app_repo)

    cmd = SubmitApplicationCommand(
        idempotency_key=uuid4(),
        program_slug="open-prog",
        guardian_name="Parent",
        guardian_email="p@example.com",
        guardian_phone=None,
        guardian_relationship=GuardianRelationship.GUARDIAN,
        learner_name="Kid",
        learner_age_years=10,
        notes=None,
        declaration_accepted=False,
    )

    coro = use_case.execute(cmd)
    with pytest.raises(DeclarationRequiredError):
        asyncio.run(coro)


def test_submit_application_age_eligibility_enforced() -> None:
    prog = _sample_program("age-bound", min_age_years=9, max_age_years=14)
    prog_repo = InMemoryProgramRepository([prog])
    app_repo = InMemoryApplicationRepository(program_repo=prog_repo)
    use_case = SubmitApplicationUseCase(prog_repo, app_repo)

    young_cmd = SubmitApplicationCommand(
        idempotency_key=uuid4(),
        program_slug="age-bound",
        guardian_name="Parent",
        guardian_email="p@example.com",
        guardian_phone=None,
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name="Younger Kid",
        learner_age_years=7,
        notes=None,
        declaration_accepted=True,
    )
    young_coro = use_case.execute(young_cmd)
    with pytest.raises(LearnerIneligibleError):
        asyncio.run(young_coro)

    old_cmd = SubmitApplicationCommand(
        idempotency_key=uuid4(),
        program_slug="age-bound",
        guardian_name="Parent",
        guardian_email="p@example.com",
        guardian_phone=None,
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name="Older Kid",
        learner_age_years=16,
        notes=None,
        declaration_accepted=True,
    )
    old_coro = use_case.execute(old_cmd)
    with pytest.raises(LearnerIneligibleError):
        asyncio.run(old_coro)


def test_submit_application_applications_closed() -> None:
    prog = _sample_program("closed-prog", applications_enabled=False)
    prog_repo = InMemoryProgramRepository([prog])
    app_repo = InMemoryApplicationRepository(program_repo=prog_repo)
    use_case = SubmitApplicationUseCase(prog_repo, app_repo)

    closed_cmd = SubmitApplicationCommand(
        idempotency_key=uuid4(),
        program_slug="closed-prog",
        guardian_name="Parent",
        guardian_email="p@example.com",
        guardian_phone=None,
        guardian_relationship=GuardianRelationship.PARENT,
        learner_name="Kid",
        learner_age_years=10,
        notes=None,
        declaration_accepted=True,
    )
    closed_coro = use_case.execute(closed_cmd)
    with pytest.raises(ApplicationsClosedError):
        asyncio.run(closed_coro)
