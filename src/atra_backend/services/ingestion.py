"""Market Data Ingestion Service."""

import asyncio
import os
import signal
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from atra_backend.api.deps import get_db
from atra_backend.api.v1.schemas import CandleCreate
from atra_backend.core.logging import get_logger, setup_logging
from atra_backend.crud import validation_crud
from atra_backend.crud.candle_crud import create_candles
from atra_backend.models.candle import Candle
from atra_backend.validation.engine import validate_candle_data


class ExchangeAdapter(ABC):
    """Abstract base exchange adapter for fetching market data."""

    @abstractmethod
    async def fetch_candles(self, symbol: str, interval: str, limit: int) -> List[List]:
        """Fetch candle data from the exchange.

        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            interval: Candlestick interval (e.g., 1m, 5m)
            limit: Number of candles to fetch

        Returns:
            List of candle data in exchange-specific format
        """
        pass

    @abstractmethod
    def convert_candle(
        self, candle_data: List, symbol: str, dataset_version: str, interval: str
    ) -> CandleCreate:
        """Convert exchange-specific candle data to our CandleCreate schema.

        Args:
            candle_data: Raw candle data from exchange
            symbol: Trading pair symbol
            dataset_version: Dataset version string
            interval: Candlestick interval (e.g., 1m, 5m)

        Returns:
            CandleCreate object
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Exchange name identifier."""
        pass


class BinanceExchangeAdapter(ExchangeAdapter):
    """Binance exchange adapter for fetching market data."""

    def __init__(self, api_url: str = "https://api.binance.com"):
        """Initialize the Binance adapter.

        Args:
            api_url: Base URL for the Binance API
        """
        self._api_url = api_url.rstrip("/")

    async def fetch_candles(self, symbol: str, interval: str, limit: int) -> List[List]:
        """Fetch candle data from Binance API.

        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            interval: Candlestick interval (e.g., 1m, 5m)
            limit: Number of candles to fetch

        Returns:
            List of candle data from Binance in format:
            [
                [
                    1499040000000,      // Open time
                    "0.01634790",       // Open
                    "0.80000000",       // High
                    "0.01575800",       // Low
                    "0.01577100",       // Close
                    "148976.11427815",  // Volume
                    1499644799999,      // Close time
                    "2434.19055334",    // Quote asset volume
                    308,                // Number of trades
                    "1756.87402397",    // Taker buy base asset volume
                    "28.46694368",      // Taker buy quote asset volume
                    "0"                 // Ignore.
                ]
            ]
        """
        endpoint = f"{self._api_url}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

        return data

    def convert_candle(
        self, candle_data: List, symbol: str, dataset_version: str, interval: str
    ) -> CandleCreate:
        """Convert Binance candle data to our CandleCreate schema.

        Args:
            candle_data: List of values from Binance kline
            symbol: Trading pair symbol
            dataset_version: Dataset version string
            interval: Candlestick interval (e.g., 1m, 5m)

        Returns:
            CandleCreate object
        """
        (
            open_time,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            close_time,
            quote_asset_volume,
            number_of_trades,
            taker_buy_base_asset_volume,
            taker_buy_quote_asset_volume,
            ignore,
        ) = candle_data

        # Convert timestamps to datetime objects in UTC
        # Binance timestamps are in milliseconds
        open_time_dt = datetime.fromtimestamp(int(open_time) / 1000, tz=timezone.utc)

        # For simplicity, we'll use open_time as the timestamp
        # In a real system, you might want to use the close time or store both
        timestamp = open_time_dt

        return CandleCreate(
            asset=symbol,
            timestamp=timestamp,
            timeframe=interval,
            open=float(open_price),
            high=float(high_price),
            low=float(low_price),
            close=float(close_price),
            volume=float(volume) if volume else 0.0,
            source="binance",
            dataset_version=dataset_version,  # Could be made configurable
        )

    @property
    def name(self) -> str:
        """Exchange name identifier."""
        return "binance"


class IngestionService:
    """Service for ingesting market data from external sources."""

    logger = get_logger(__name__)

    def __init__(
        self,
        symbols: List[str],
        interval: str = "1m",
        limit: int = 500,
        fetch_interval_seconds: int = 60,
        api_url: str = "https://api.binance.com",
        exchange_adapter: Optional[ExchangeAdapter] = None,
    ):
        """
        Initialize the ingestion service.

        Args:
            symbols: List of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"])
            interval: Candlestick interval (e.g., "1m", "5m", "1h", "1d")
            limit: Number of candles to fetch per request
            fetch_interval_seconds: How often to fetch data (in seconds)
            api_url: Base URL for the exchange API (used if exchange_adapter not provided)
            exchange_adapter: Exchange adapter instance (if provided, overrides api_url)
        """
        self.symbols = [s.upper() for s in symbols]
        self.interval = interval
        self.limit = limit
        self.fetch_interval_seconds = fetch_interval_seconds

        # Set up exchange adapter
        if exchange_adapter is not None:
            self.exchange_adapter = exchange_adapter
        else:
            self.exchange_adapter = BinanceExchangeAdapter(api_url=api_url)

        self._running = False
        self._task: Optional[asyncio.Task] = None

        # Metrics for monitoring
        self._cycles_completed = 0
        self._total_candles_ingested = 0
        self._total_validation_failures = 0
        self._last_metrics_log_time = None
        self._metrics_log_interval = 300  # Log metrics every 5 minutes (300 seconds)

    async def _get_async_session(self) -> AsyncSession:
        """Get an async database session."""
        # We'll reuse the same pattern as in api/deps.py
        from atra_backend.api.deps import _get_session_factory

        AsyncSessionLocal = _get_session_factory()
        return AsyncSessionLocal()

    async def store_and_validate_candles(
        self, session: AsyncSession, candles: List[CandleCreate]
    ) -> List[Candle]:
        """
        Store candles in the database and run validation on them.

        Args:
            session: Async database session
            candles: List of CandleCreate objects

        Returns:
            List of stored Candle objects (with IDs populated)
        """
        # Insert candles into the database
        db_candles = await create_candles(db=session, candles_in=candles)

        # Validate each candle and store validation results
        for candle in db_candles:
            validation_results = await validate_candle_data(session, candle)
            # Store validation results in the database
            if validation_results:
                await validation_crud.create_validation_results(
                    session, validation_results
                )

            # Log failed validations for monitoring
            failed_results = [r for r in validation_results if not r.is_valid]
            if failed_results:
                self.logger.warning(
                    f"Validation failed for {len(failed_results)} rules on candle {candle.id} "
                    f"({candle.asset}/{candle.timeframe}). Failed rules: {[r.validation_rule for r in failed_results]}"
                )
                # Increment validation failure counter
                self._total_validation_failures += len(failed_results)

        return db_candles

    async def fetch_and_store_symbol(self, session: AsyncSession, symbol: str) -> None:
        """
        Fetch and store candles for a single symbol.

        Args:
            session: Async database session
            symbol: Trading pair symbol
        """
        try:
            # Fetch data from exchange adapter
            raw_candles = await self.exchange_adapter.fetch_candles(
                symbol=symbol,
                interval=self.interval,
                limit=self.limit,
            )

            # Convert to our schema
            dataset_version = (
                f"ingest_{datetime.now(timezone.utc).isoformat(timespec='seconds')}"
            )
            candles_to_store = []
            for raw_candle in raw_candles:
                candle_create = self.exchange_adapter.convert_candle(
                    raw_candle, symbol, dataset_version, self.interval
                )
                candles_to_store.append(candle_create)

            # Store and validate
            await self.store_and_validate_candles(session, candles_to_store)

            # Log success
            self.logger.info(
                f"[{datetime.now(timezone.utc).isoformat()}] "
                f"Ingested {len(candles_to_store)} candles for {symbol}"
            )
            # Increment candles ingested counter
            self._total_candles_ingested += len(candles_to_store)
        except Exception as e:
            self.logger.error(f"Error ingesting data for {symbol}: {e}")

    async def run_ingestion_cycle(self) -> None:
        """Run one iteration of fetching and storing data for all symbols."""
        # Get a database session
        async for session in get_db():
            # Process each symbol
            for symbol in self.symbols:
                await self.fetch_and_store_symbol(session, symbol)
            # Commit the session (the get_db generator will close the session)
            break  # We only need one session for this cycle

        # Increment cycles completed
        self._cycles_completed += 1

        # Check if it's time to log metrics
        now = datetime.now(timezone.utc)
        if (
            self._last_metrics_log_time is None
            or (now - self._last_metrics_log_time).total_seconds()
            >= self._metrics_log_interval
        ):
            await self._log_metrics(now)
            self._last_metrics_log_time = now

    async def _log_metrics(self, now: datetime) -> None:
        """Log periodic metrics about the ingestion service."""
        self.logger.info(
            f"Ingestion service metrics - "
            f"Cycles: {self._cycles_completed}, "
            f"Candles ingested: {self._total_candles_ingested}, "
            f"Validation failures: {self._total_validation_failures}"
        )

    async def start(self) -> None:
        """Start the ingestion service loop."""
        if self._running:
            return

        self._running = True
        self.logger.info("Starting ingestion service...")
        while self._running:
            start_time = datetime.now(timezone.utc)
            await self.run_ingestion_cycle()
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            sleep_time = max(0, self.fetch_interval_seconds - elapsed)
            await asyncio.sleep(sleep_time)

    def stop(self) -> None:
        """Stop the ingestion service loop."""
        self._running = False
        if self._task:
            self._task.cancel()
        self.logger.info("Stopping ingestion service...")


async def main() -> None:
    """Main entry point for running the ingestion service."""
    # Setup logging
    setup_logging()

    # Get configuration from environment variables with defaults
    symbols_str = os.getenv("INGESTION_SYMBOLS", "BTCUSDT,ETHUSDT")
    symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
    interval = os.getenv("INGESTION_INTERVAL", "1m")
    limit = int(os.getenv("INGESTION_LIMIT", "500"))
    fetch_interval_seconds = int(os.getenv("INGESTION_INTERVAL_SECONDS", "60"))
    api_url = os.getenv("INGESTION_API_URL", "https://api.binance.com")

    service = IngestionService(
        symbols=symbols,
        interval=interval,
        limit=limit,
        fetch_interval_seconds=fetch_interval_seconds,
        api_url=api_url,
    )

    # Setup signal handlers for graceful shutdown
    def signal_handler():
        service.logger.info("Received shutdown signal")
        service.stop()

    # Register signal handlers
    try:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, signal_handler)
        loop.add_signal_handler(signal.SIGINT, signal_handler)
    except NotImplementedError:
        # Signal handlers not available on Windows
        service.logger.warning("Signal handlers not available on this platform")

    try:
        await service.start()
    except KeyboardInterrupt:
        service.logger.info("Received KeyboardInterrupt")
    except Exception as e:
        service.logger.error(f"Ingestion service error: {e}")
    finally:
        service.logger.info("Shutting down ingestion service")
        service.stop()


if __name__ == "__main__":
    asyncio.run(main())
