"""API Schemas."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class CandleBase(BaseModel):
    """Base candle schema."""
    asset: str = Field(..., max_length=20)
    timeframe: str = Field(..., max_length=10)
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Optional[Decimal] = None
    source: str = Field(..., max_length=50)
    dataset_version: str = Field(..., max_length=20)


class CandleCreate(CandleBase):
    """Schema for creating a candle."""
    pass


class CandleUpdate(BaseModel):
    """Schema for updating a candle."""
    asset: Optional[str] = Field(None, max_length=20)
    timeframe: Optional[str] = Field(None, max_length=10)
    timestamp: Optional[datetime] = None
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    source: Optional[str] = Field(None, max_length=50)
    dataset_version: Optional[str] = Field(None, max_length=20)


# Rebuild model to resolve any forward references
CandleUpdate.model_rebuild()


class CandleInDBBase(CandleBase):
    """Base schema for candle stored in DB."""
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class Candle(CandleInDBBase):
    """Schema for candle response."""
    pass


class CandleList(BaseModel):
    """Schema for paginated candle list."""
    items: List[Candle]
    total: int
    page: int
    size: int
    pages: int


class MarketDataRequest(BaseModel):
    """Schema for market data requests."""
    asset: str = Field(..., max_length=20)
    timeframe: str = Field(..., max_length=10)
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None
    limit: Optional[int] = Field(None, gt=0, le=10000)


    @validator('from_time', 'to_time')
    def validate_times(cls, v):
        return v

    @validator('to_time')
    def to_time_after_from_time(cls, v, values):
        if v and values.get('from_time') and v < values['from_time']:
            raise ValueError('to_time must be after from_time')
        return v