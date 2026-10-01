"""Candle Model."""

from sqlalchemy import Column, DateTime, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from atra_backend.models.base import Base


class Candle(Base):
    """Candle model representing OHLCV market data."""

    __tablename__ = "candles"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    asset = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Numeric(precision=20, scale=8), nullable=False)
    high = Column(Numeric(precision=20, scale=8), nullable=False)
    low = Column(Numeric(precision=20, scale=8), nullable=False)
    close = Column(Numeric(precision=20, scale=8), nullable=False)
    volume = Column(Numeric(precision=20, scale=8), nullable=True)
    source = Column(String(50), nullable=False)
    dataset_version = Column(String(20), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Candle {self.asset}/{self.timeframe} {self.timestamp} O:{self.open} H:{self.high} L:{self.low} C:{self.close}>"
