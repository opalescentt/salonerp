"""Smoke test for the app factory + scaffolding. Not a real feature test —
just proves the app boots and dependency wiring (settings → app) works."""

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
