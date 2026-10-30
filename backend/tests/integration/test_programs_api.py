"""Integration tests for programs catalogue and application submission endpoints."""

from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.bootstrap import create_app
from app.config import Settings
from app.modules.programs.domain.entities import Program
from app.modules.programs.domain.values import (
    Pathway,
    ProgramDelivery,
    ProgramStatus,
)
from app.modules.programs.infrastructure.in_memory import (
    InMemoryApplicationRepository,
    InMemoryProgramRepository,
)


@pytest.fixture
def program_repo() -> InMemoryProgramRepository:
    now = datetime.now(UTC)
    p1 = Program(
        id=uuid4(),
        pathway=Pathway.SATURDAY_CLUB,
        title="Saturday Robotics",
        slug="saturday-robotics",
        summary="Robotics and embedded electronics",
        description="Build and code real microcontrollers and sensors.",
        delivery=ProgramDelivery.IN_PERSON,
        status=ProgramStatus.PUBLISHED,
        applications_enabled=True,
        applications_open_at=now - timedelta(days=1),
        applications_close_at=now + timedelta(days=30),
        starts_on=date(2027, 1, 9),
        ends_on=date(2027, 4, 10),
        max_enrolments=20,
        min_age_years=8,
        max_age_years=15,
        display_order=1,
        created_at=now,
        updated_at=now,
    )
    p2 = Program(
        id=uuid4(),
        pathway=Pathway.SCHOOL_TERM,
        title="School Term Code",
        slug="school-term-code",
        summary="Term-time programming",
        description="Python foundations and computational thinking.",
        delivery=ProgramDelivery.IN_PERSON,
        status=ProgramStatus.PUBLISHED,
        applications_enabled=False,
        applications_open_at=None,
        applications_close_at=None,
        starts_on=date(2027, 1, 15),
        ends_on=date(2027, 4, 5),
        max_enrolments=30,
        min_age_years=10,
        max_age_years=16,
        display_order=2,
        created_at=now,
        updated_at=now,
    )
    p_single = Program(
        id=uuid4(),
        pathway=Pathway.HOLIDAY,
        title="Python Single Char Camp",
        slug="p",
        summary="One char slug test",
        description="Validating single character slug support.",
        delivery=ProgramDelivery.ONLINE,
        status=ProgramStatus.PUBLISHED,
        applications_enabled=True,
        applications_open_at=None,
        applications_close_at=None,
        starts_on=date(2027, 5, 1),
        ends_on=date(2027, 5, 10),
        max_enrolments=15,
        min_age_years=None,
        max_age_years=None,
        display_order=3,
        created_at=now,
        updated_at=now,
    )
    return InMemoryProgramRepository([p1, p2, p_single])


@pytest.fixture
def application_repo(
    program_repo: InMemoryProgramRepository,
) -> InMemoryApplicationRepository:
    return InMemoryApplicationRepository(program_repo=program_repo)


@pytest.fixture
def app_client(
    program_repo: InMemoryProgramRepository,
    application_repo: InMemoryApplicationRepository,
) -> TestClient:
    app = create_app(
        Settings(_env_file=None, environment="test", cors_origins=["http://localhost:3000"]),
        program_repository=program_repo,
        application_repository=application_repo,
    )
    return TestClient(app)


def test_list_programs_returns_published_items(app_client: TestClient) -> None:
    response = app_client.get("/api/v1/programs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["items"][0]["slug"] == "saturday-robotics"


def test_list_programs_filters_by_pathway(app_client: TestClient) -> None:
    response = app_client.get("/api/v1/programs?pathway=saturday_club")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["slug"] == "saturday-robotics"


def test_get_program_by_slug(app_client: TestClient) -> None:
    response = app_client.get("/api/v1/programs/saturday-robotics")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "saturday-robotics"
    assert "description" in data


def test_get_single_character_slug(app_client: TestClient) -> None:
    response = app_client.get("/api/v1/programs/p")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "p"


def test_get_program_not_found_returns_problem_details(app_client: TestClient) -> None:
    response = app_client.get("/api/v1/programs/unknown-slug")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["status"] == 404
    assert response.json()["title"] == "Program Not Found"


def test_submit_application_success_and_idempotent_replay(app_client: TestClient) -> None:
    idempotency_key = str(uuid4())
    payload = {
        "idempotency_key": idempotency_key,
        "guardian_name": "Wangari Maathai",
        "guardian_email": "wangari@example.com",
        "guardian_phone": "+254700112233",
        "guardian_relationship": "parent",
        "learner_name": "Wanjiru",
        "learner_age_years": 10,
        "notes": "Excited for Saturday class",
        "declaration_accepted": True,
        "declaration_version": 1,
    }

    # 1. First submission -> 201 Created
    response1 = app_client.post(
        "/api/v1/programs/saturday-robotics/applications",
        json=payload,
    )
    assert response1.status_code == 201
    data1 = response1.json()
    assert data1["reference"].startswith("JC-")
    assert data1["is_retry"] is False

    # 2. Replay with identical payload -> 200 OK
    response2 = app_client.post(
        "/api/v1/programs/saturday-robotics/applications",
        json=payload,
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["id"] == data1["id"]
    assert data2["reference"] == data1["reference"]
    assert data2["is_retry"] is True


def test_submit_application_conflict_on_reused_key(app_client: TestClient) -> None:
    idempotency_key = str(uuid4())
    payload = {
        "idempotency_key": idempotency_key,
        "guardian_name": "Wangari Maathai",
        "guardian_email": "wangari@example.com",
        "guardian_relationship": "parent",
        "learner_name": "Wanjiru",
        "learner_age_years": 10,
        "declaration_accepted": True,
        "declaration_version": 1,
    }

    # First call succeeds
    res1 = app_client.post("/api/v1/programs/saturday-robotics/applications", json=payload)
    assert res1.status_code == 201

    # Reused key with different learner
    payload_conflict = {**payload, "learner_name": "Different Learner"}
    res2 = app_client.post(
        "/api/v1/programs/saturday-robotics/applications",
        json=payload_conflict,
    )
    assert res2.status_code == 409
    assert res2.headers["content-type"].startswith("application/problem+json")
    assert res2.json()["title"] == "Idempotency Conflict"


def test_submit_application_closed_program(app_client: TestClient) -> None:
    payload = {
        "idempotency_key": str(uuid4()),
        "guardian_name": "Guardian Name",
        "guardian_email": "g@example.com",
        "guardian_relationship": "guardian",
        "learner_name": "Learner",
        "learner_age_years": 12,
        "declaration_accepted": True,
        "declaration_version": 1,
    }
    # school-term-code has applications_enabled = False
    response = app_client.post(
        "/api/v1/programs/school-term-code/applications",
        json=payload,
    )
    assert response.status_code == 422
    assert response.json()["title"] == "Applications Closed"


def test_submit_application_whitespace_rejected(app_client: TestClient) -> None:
    payload = {
        "idempotency_key": str(uuid4()),
        "guardian_name": "    ",
        "guardian_email": "g@example.com",
        "guardian_relationship": "parent",
        "learner_name": "Learner",
        "learner_age_years": 10,
        "declaration_accepted": True,
        "declaration_version": 1,
    }
    response = app_client.post(
        "/api/v1/programs/saturday-robotics/applications",
        json=payload,
    )
    assert response.status_code == 422


def test_submit_application_cors_and_request_id(app_client: TestClient) -> None:
    response = app_client.get(
        "/api/v1/programs",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "X-Request-ID" in response.headers
