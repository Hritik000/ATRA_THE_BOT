"""Unit tests for the Data Validation Engine and endpoints."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

from atra_backend.models.candle import Candle
from atra_backend.validation.engine import ValidationEngine


def create_sample_candle(
    open_price: str = "50000.00",
    high_price: str = "51000.00",
    low_price: str = "49000.00",
    close_price: str = "50500.00",
    volume: str = "10.5",
    source: str = "binance",
    dataset_version: str = "v1.0",
) -> Candle:
    """Helper to instantiate a Candle model instance for testing."""
    return Candle(
        id=uuid4(),
        asset="BTC",
        timeframe="1h",
        timestamp=datetime.now(timezone.utc),
        open=Decimal(open_price),
        high=Decimal(high_price),
        low=Decimal(low_price),
        close=Decimal(close_price),
        volume=Decimal(volume) if volume is not None else None,
        source=source,
        dataset_version=dataset_version,
    )


def test_validation_engine_valid_candle():
    """Test that a valid candle passes all validation checks."""
    mock_db = AsyncMock()
    engine = ValidationEngine(db=mock_db)

    candle = create_sample_candle()
    results = asyncio.run(engine.validate_candle(candle))

    # All returned checks should be valid
    invalid_results = [r for r in results if not r.is_valid]
    assert len(invalid_results) == 0, (
        f"Expected all checks to pass, failed: {invalid_results}"
    )


def test_validation_engine_invalid_high_low():
    """Test that high < low is flagged as critical/error."""
    mock_db = AsyncMock()
    engine = ValidationEngine(db=mock_db)

    # Invalid: high (48000) < low (49000)
    candle = create_sample_candle(high_price="48000.00", low_price="49000.00")
    results = asyncio.run(engine.validate_candle(candle))

    invalid_results = [r for r in results if not r.is_valid]
    assert len(invalid_results) > 0
    rule_names = [r.validation_rule for r in invalid_results]
    assert "high_gte_low" in rule_names


def test_validation_engine_negative_price():
    """Test that negative prices are flagged as invalid."""
    mock_db = AsyncMock()
    engine = ValidationEngine(db=mock_db)

    candle = create_sample_candle(open_price="-100.00", low_price="-200.00")
    results = asyncio.run(engine.validate_candle(candle))

    invalid_results = [r for r in results if not r.is_valid]
    assert len(invalid_results) > 0


def test_validation_engine_negative_volume():
    """Test that negative volume is flagged."""
    mock_db = AsyncMock()
    engine = ValidationEngine(db=mock_db)

    candle = create_sample_candle(volume="-5.0")
    results = asyncio.run(engine.validate_candle(candle))

    invalid_results = [r for r in results if not r.is_valid]
    assert len(invalid_results) > 0
    assert any("volume" in r.validation_rule.lower() for r in invalid_results)


def test_validation_endpoints_empty_list(client: TestClient):
    """Test fetching validation results when none exist."""
    response = client.get("/api/v1/validation")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["items"] == []


def test_validation_endpoint_not_found(client: TestClient):
    """Test fetching a non-existent validation result by ID."""
    random_id = str(uuid4())
    response = client.get(f"/api/v1/validation/{random_id}")
    assert response.status_code == 404
