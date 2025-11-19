"""Tests for API endpoints.

Тесты для всех REST API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_api_analyze_endpoint(client: TestClient) -> None:
    """Test /api/v1/analyze endpoint."""
    response = client.post(
        "/api/v1/analyze",
        json={
            "disease_name": "грипп",
            "region": "Санкт-Петербург",
            "days": 7,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "disease_name" in data


def test_api_forecast_endpoint(client: TestClient) -> None:
    """Test /api/v1/forecast endpoint."""
    response = client.post(
        "/api/v1/forecast",
        json={
            "disease_name": "грипп",
            "forecast_days": 14,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data


def test_api_health_endpoint(client: TestClient) -> None:
    """Test /api/v1/health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_api_metrics_endpoint(client: TestClient) -> None:
    """Test /api/v1/metrics endpoint."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
