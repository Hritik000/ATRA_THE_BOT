"""Candle Endpoint Tests."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient


def test_get_candles_endpoint(client: TestClient):
    """Test get candles endpoint."""
    response = client.get(
        "/api/v1/market", params={"asset": "BTC", "timeframe": "1h", "limit": 10}
    )
    # Since we're using mocked database, we expect 200 (empty list)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert data["items"] == []
    assert data["total"] == 0


def test_get_latest_candle_endpoint(client: TestClient):
    """Test get latest candle endpoint."""
    response = client.get(
        "/api/v1/market/latest", params={"asset": "ETH", "timeframe": "1h"}
    )
    # Since we're using mocked database, we expect 200 (null - no data)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    # Could be None (no data) or a candle object
    assert response.json() is None or isinstance(response.json(), dict)


def test_create_candle_endpoint(client: TestClient):
    """Test create candle endpoint."""
    candle_data = {
        "asset": "BTC",
        "timeframe": "1h",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "open": "50000.00",
        "high": "51000.00",
        "low": "49000.00",
        "close": "50500.00",
        "volume": "100.5",
        "source": "binance",
        "dataset_version": "v1.0",
    }

    response = client.post("/api/v1/market", json=candle_data)
    # Since we're using mocked database, we expect 201 (created)
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert "id" in data
    assert data["asset"] == "BTC"
    assert data["timeframe"] == "1h"


def test_market_data_request_validation(client: TestClient):
    """Test market data request validation."""
    # Test valid request
    response = client.get(
        "/api/v1/market", params={"asset": "BTC", "timeframe": "1h", "limit": 100}
    )
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"

    # Test invalid limit (too high)
    response = client.get(
        "/api/v1/market",
        params={
            "asset": "BTC",
            "timeframe": "1h",
            "limit": 15000,  # Above max of 10000
        },
    )
    assert (
        response.status_code == 422
    ), f"Expected 422 for validation error, got {response.status_code}: {response.text}"

    # Test invalid time range
    response = client.get(
        "/api/v1/market",
        params={
            "asset": "BTC",
            "timeframe": "1h",
            "from_time": "2026-10-01T12:00:00Z",
            "to_time": "2026-10-01T10:00:00Z",  # Before from_time
        },
    )
    assert (
        response.status_code == 400
    ), f"Expected 400 for bad request, got {response.status_code}: {response.text}"
