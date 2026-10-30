"""Use explicit test settings so local credentials never affect the suite."""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.bootstrap import create_app
from app.config import Settings

# Only the explicit, isolated database-test variables survive the per-test cleanup below.
# LMS_DATABASE_URL (the runtime database) is deliberately NOT in this list.
_PRESERVED_TEST_VARIABLES = frozenset(
    {
        "LMS_TEST_DATABASE_URL",
        "LMS_TEST_MAINTENANCE_DATABASE_URL",
        "LMS_REQUIRE_DATABASE_TESTS",
    }
)


@pytest.fixture(autouse=True)
def isolate_lms_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.startswith("LMS_") and name not in _PRESERVED_TEST_VARIABLES:
            monkeypatch.delenv(name)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app(Settings(_env_file=None, environment="test"))) as test_client:
        yield test_client
