"""API Schemas."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


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

    model_config = ConfigDict(from_attributes=True)


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


# Validation Schemas
class ValidationResultBase(BaseModel):
    """Base validation result schema."""
    validation_type: str
    validation_rule: str
    is_valid: bool
    severity: str  # info, warning, error, critical
    message: Optional[str] = None
    actual_value: Optional[str] = None
    expected_value: Optional[str] = None
    validation_metadata: Optional[Dict[str, Any]] = None


class ValidationResultCreate(ValidationResultBase):
    """Schema for creating a validation result."""
    candle_id: Optional[UUID] = None
    batch_id: Optional[str] = None


class ValidationResultInDBBase(ValidationResultBase):
    """Base schema for validation result stored in DB."""
    id: UUID
    candle_id: Optional[UUID] = None
    batch_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ValidationResult(ValidationResultInDBBase):
    """Schema for validation result response."""
    pass


class ValidationResultList(BaseModel):
    """Schema for paginated validation result list."""
    items: List[ValidationResult]
    total: int
    page: int
    size: int
    pages: int


class ValidationRequest(BaseModel):
    """Schema for validation requests."""
    candle_ids: Optional[List[UUID]] = None
    batch_id: Optional[str] = None
    validation_types: Optional[List[str]] = None
    rules: Optional[List[str]] = None


class MarketDataRequest(BaseModel):
    """Schema for market data requests."""
    asset: str = Field(..., max_length=20)
    timeframe: str = Field(..., max_length=10)
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None
    limit: Optional[int] = Field(None, gt=0, le=10000)

    @model_validator(mode='after')
    def to_time_after_from_time(self):
        if self.to_time and self.from_time and self.to_time < self.from_time:
            raise ValueError('to_time must be after from_time')
        return self