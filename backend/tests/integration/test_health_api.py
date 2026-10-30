"""Verify infrastructure failures and cross-origin error contracts."""

from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.bootstrap import create_app
from app.config import Settings


class FakeProbe:
    def __init__(self, available: bool) -> None:
        self.available = available

    async def ping(self) -> bool:
        return self.available


def test_liveness_remains_available_without_database(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    UUID(response.headers["X-Request-ID"])


def test_readiness_reports_unconfigured_database(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


@pytest.mark.parametrize("available, expected", [(True, 200), (False, 503)])
def test_readiness_uses_injected_probe(available: bool, expected: int) -> None:
    app = create_app(Settings(_env_file=None, environment="test"), FakeProbe(available))
    with TestClient(app) as client:
        assert client.get("/api/v1/health/ready").status_code == expected


def test_missing_routes_use_problem_details(client: TestClient) -> None:
    response = client.get("/api/v1/not-a-resource")
    assert response.status_code == 404
    assert response.json()["status"] == 404
    assert response.headers["content-type"].startswith("application/problem+json")


def test_browser_origin_allowlist(client: TestClient) -> None:
    allowed = client.get("/api/v1/health/live", headers={"Origin": "http://localhost:3000"})
    denied = client.get("/api/v1/health/live", headers={"Origin": "https://untrusted.example"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-origin" not in denied.headers


def test_unexpected_failure_is_redacted_and_has_cors() -> None:
    app: FastAPI = create_app(Settings(_env_file=None, environment="test"))

    @app.get("/test/failure")
    async def fail() -> None:
        raise RuntimeError("private-connection-password")

    with TestClient(app) as client:
        response = client.get("/test/failure", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 500
    assert "private-connection-password" not in response.text
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
