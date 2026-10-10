"""Tests for the ingestion service and exchange adapters."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from atra_backend.api.v1.schemas import CandleCreate
from atra_backend.services.ingestion import (
    BinanceExchangeAdapter,
    ExchangeAdapter,
    IngestionService,
)


def test_exchange_adapter_abstract_base_class():
    """Test that ExchangeAdapter cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ExchangeAdapter()  # type: ignore


def test_binance_exchange_adapter_init():
    """Test BinanceExchangeAdapter initialization."""
    adapter = BinanceExchangeAdapter(api_url="https://test.binance.com")
    assert adapter._api_url == "https://test.binance.com"

    # Default init
    adapter_default = BinanceExchangeAdapter()
    assert adapter_default._api_url == "https://api.binance.com"


@pytest.mark.asyncio
async def test_binance_exchange_adapter_fetch_candles():
    """Test fetching candles from BinanceExchangeAdapter."""
    adapter = BinanceExchangeAdapter()
    mock_response = MagicMock()
    mock_response.json.return_value = [
        [
            1499040000000,
            "0.01634790",
            "0.80000000",
            "0.01575800",
            "0.01577100",
            "148976.11427815",
            1499644799999,
            "2434.19055334",
            308,
            "1756.87402397",
            "28.46694368",
            "0",
        ]
    ]
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        result = await adapter.fetch_candles("BTCUSDT", "1m", 1)
        mock_get.assert_called_once_with(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": "BTCUSDT", "interval": "1m", "limit": 1},
        )
        assert result == [
            [
                1499040000000,
                "0.01634790",
                "0.80000000",
                "0.01575800",
                "0.01577100",
                "148976.11427815",
                1499644799999,
                "2434.19055334",
                308,
                "1756.87402397",
                "28.46694368",
                "0",
            ]
        ]


def test_binance_exchange_adapter_convert_candle():
    """Test converting Binance candle data to CandleCreate."""
    adapter = BinanceExchangeAdapter()
    candle_data = [
        1499040000000,  # Open time
        "0.01634790",  # Open
        "0.80000000",  # High
        "0.01575800",  # Low
        "0.01577100",  # Close
        "148976.11427815",  # Volume
        1499644799999,  # Close time
        "2434.19055334",  # Quote asset volume
        308,  # Number of trades
        "1756.87402397",  # Taker buy base asset volume
        "28.46694368",  # Taker buy quote asset volume
        "0",  # Ignore.
    ]
    symbol = "BTCUSDT"
    dataset_version = "test_version"
    interval = "1m"

    candle_create = adapter.convert_candle(
        candle_data, symbol, dataset_version, interval
    )

    assert isinstance(candle_create, CandleCreate)
    assert candle_create.asset == symbol
    assert candle_create.timeframe == interval
    assert candle_create.timestamp == datetime.fromtimestamp(
        1499040000000 / 1000, tz=timezone.utc
    )
    assert candle_create.open == Decimal("0.01634790")
    assert candle_create.high == Decimal("0.80000000")
    assert candle_create.low == Decimal("0.01575800")
    assert candle_create.close == Decimal("0.01577100")
    assert candle_create.volume == Decimal("148976.11427815")
    assert candle_create.source == "binance"
    assert candle_create.dataset_version == dataset_version


def test_ingestion_service_init():
    """Test IngestionService initialization."""
    # With default adapter (Binance)
    service = IngestionService(symbols=["BTCUSDT"], interval="1m")
    assert service.symbols == ["BTCUSDT"]
    assert service.interval == "1m"
    assert service.limit == 500
    assert service.fetch_interval_seconds == 60
    assert isinstance(service.exchange_adapter, BinanceExchangeAdapter)
    assert service.exchange_adapter._api_url == "https://api.binance.com"

    # With custom adapter
    custom_adapter = BinanceExchangeAdapter(api_url="https://custom.api")
    service_custom = IngestionService(
        symbols=["ETHUSDT"],
        interval="5m",
        limit=100,
        fetch_interval_seconds=30,
        exchange_adapter=custom_adapter,
    )
    assert service_custom.symbols == ["ETHUSDT"]
    assert service_custom.interval == "5m"
    assert service_custom.limit == 100
    assert service_custom.fetch_interval_seconds == 30
    assert service_custom.exchange_adapter is custom_adapter
    assert service_custom.exchange_adapter._api_url == "https://custom.api"

    # With api_url and no custom adapter (should create Binance adapter with that URL)
    service_api_url = IngestionService(
        symbols=["BTCUSDT"],
        api_url="https://api.example.com",
    )
    assert isinstance(service_api_url.exchange_adapter, BinanceExchangeAdapter)
    assert service_api_url.exchange_adapter._api_url == "https://api.example.com"


@pytest.mark.asyncio
async def test_ingestion_service_store_and_validate_candles(
    mock_db_session: AsyncSession,
):
    """Test storing and validating candles."""
    service = IngestionService(symbols=["BTCUSDT"], fetch_interval_seconds=0)
    # Mock the validation engine to return some results
    mock_validation_results = [
        MagicMock(is_valid=True),
        MagicMock(is_valid=False, validation_rule="test_rule"),
    ]

    with (
        patch(
            "atra_backend.services.ingestion.validate_candle_data",
            return_value=mock_validation_results,
        ),
        patch("atra_backend.services.ingestion.create_candles") as mock_create_candles,
        patch(
            "atra_backend.services.ingestion.validation_crud.create_validation_results"
        ) as mock_create_val,
    ):
        # Mock create_candles to return some candle objects
        mock_candles = [MagicMock(id=1), MagicMock(id=2)]
        mock_create_candles.return_value = mock_candles

        # Input candles to store
        candles_in = [
            CandleCreate(
                asset="BTC",
                timeframe="1m",
                timestamp=datetime.now(timezone.utc),
                open=1.0,
                high=2.0,
                low=0.5,
                close=1.5,
                volume=10.0,
                source="test",
                dataset_version="test",
            )
        ]

        result = await service.store_and_validate_candles(mock_db_session, candles_in)

        # Check that create_candles was called with the correct arguments
        mock_create_candles.assert_called_once_with(
            db=mock_db_session, candles_in=candles_in
        )
        # Check that validation results were created for each candle
        assert mock_create_val.call_count == len(mock_candles)
        # Check that the function returns the mock candles
        assert result == mock_candles


@pytest.mark.asyncio
async def test_ingestion_service_run_ingestion_cycle(mock_db_session: AsyncSession):
    """Test one ingestion cycle."""
    service = IngestionService(symbols=["BTCUSDT"], limit=1)
    # Mock the exchange adapter
    service.exchange_adapter = AsyncMock()
    service.exchange_adapter.fetch_candles.return_value = [
        [
            1499040000000,
            "0.01634790",
            "0.80000000",
            "0.01575800",
            "0.01577100",
            "148976.11427815",
            1499644799999,
            "2434.19055334",
            308,
            "1756.87402397",
            "28.46694368",
            "0",
        ]
    ]
    service.exchange_adapter.convert_candle.return_value = CandleCreate(
        asset="BTCUSDT",
        timeframe="1m",
        timestamp=datetime.now(timezone.utc),
        open=0.01634790,
        high=0.80000000,
        low=0.01575800,
        close=0.01577100,
        volume=148976.11427815,
        source="binance",
        dataset_version="test_version",
    )

    # Mock the store_and_validate_candles method
    service.store_and_validate_candles = AsyncMock()

    # Mock the session getter
    with patch.object(service, "_get_async_session", return_value=mock_db_session):
        await service.run_ingestion_cycle()

    # Check that fetch_candles was called
    service.exchange_adapter.fetch_candles.assert_called_once_with(
        symbol="BTCUSDT",
        interval="1m",
        limit=1,
    )
    # Check that convert_candle was called for each raw candle
    assert service.exchange_adapter.convert_candle.call_count == 1
    # Check that store_and_validate_candles was called
    service.store_and_validate_candles.assert_called_once()
    # Check that metrics were updated (cycles completed and candles ingested)
    assert service._cycles_completed == 1
    assert service._total_candles_ingested == 1


def test_ingestion_service_start_stop():
    """Test starting and stopping the ingestion service."""
    service = IngestionService(symbols=["BTCUSDT"], fetch_interval_seconds=0)
    assert not service._running
    assert service._task is None

    # Mock the run_ingestion_cycle to avoid infinite loop
    service.run_ingestion_cycle = AsyncMock()

    # Start the service (we'll run it briefly and then stop)
    import asyncio

    async def test_start_stop():
        task = asyncio.create_task(service.start())
        # Give it a moment to start
        await asyncio.sleep(0.1)
        service.stop()
        await task

    asyncio.run(test_start_stop())

    # After stopping, _running should be False
    assert not service._running


if __name__ == "__main__":
    pytest.main([__file__])
