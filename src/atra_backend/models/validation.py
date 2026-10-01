"""Validation Models."""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, Float, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from atra_backend.models.base import Base


class ValidationResult(Base):
    """Validation result for a dataset or batch of data."""

    __tablename__ = "validation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    # What was validated
    candle_id = Column(UUID(as_uuid=True), ForeignKey("candles.id"), nullable=True)
    batch_id = Column(String(100), nullable=True)  # For batch validations
    # Validation metadata
    validation_type = Column(String(50), nullable=False)  # e.g., 'candle_quality', 'ohlc_logic'
    validation_rule = Column(String(100), nullable=False)  # Specific rule that was checked
    # Validation outcome
    is_valid = Column(Boolean, nullable=False)
    severity = Column(String(20), nullable=False)  # 'info', 'warning', 'error', 'critical'
    message = Column(Text, nullable=True)
    # Optional values/context
    actual_value = Column(String(500), nullable=True)
    expected_value = Column(String(500), nullable=True)
    validation_metadata = Column(JSONB, nullable=True)  # Additional context
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ValidationResult {self.validation_rule}: {self.is_valid} ({self.severity})>"