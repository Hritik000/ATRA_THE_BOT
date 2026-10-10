"""Validation Engine."""

import logging
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from atra_backend.models.candle import Candle
from atra_backend.models.validation import ValidationResult

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Engine for validating candle data quality."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_candle(self, candle: Candle) -> List[ValidationResult]:
        """
        Run all validation rules on a single candle.

        Returns:
            List of validation results (both passed and failed)
        """
        results = []

        # Run all validation rules
        validation_methods = [
            self._validate_ohlc_logic,
            self._validate_volume_non_negative,
            self._validate_timestamp_sequence,
            self._validate_price_ranges,
            self._validate_source_and_version,
        ]

        for method in validation_methods:
            try:
                method_results = await method(candle)
                results.extend(method_results)
            except Exception as e:
                logger.error(f"Error running validation {method.__name__}: {e}")
                # Create a validation error for the validation system itself
                results.append(
                    await self._create_validation_error(
                        candle_id=candle.id,
                        validation_type="validation_system",
                        validation_rule=method.__name__,
                        is_valid=False,
                        severity="critical",
                        message=f"Validation rule execution failed: {str(e)}",
                        actual_value=None,
                        expected_value="Validation rule should execute without error",
                    )
                )

        return results

    async def validate_candles(self, candles: List[Candle]) -> List[ValidationResult]:
        """
        Run validation on multiple candles.

        Returns:
            List of all validation results
        """
        all_results = []

        for candle in candles:
            candle_results = await self.validate_candle(candle)
            all_results.extend(candle_results)

        return all_results

    async def _validate_ohlc_logic(self, candle: Candle) -> List[ValidationResult]:
        """Validate OHLC logic: high >= low, high >= open/close, low <= open/close."""
        results = []

        # High should be >= Low
        if candle.high < candle.low:
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="high_gte_low",
                    is_valid=False,
                    severity="error",
                    message="High price is less than low price",
                    actual_value=f"high={candle.high}, low={candle.low}",
                    expected_value="high >= low",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="high_gte_low",
                    message="High price is greater than or equal to low price",
                    actual_value=f"high={candle.high}, low={candle.low}",
                )
            )

        # High should be >= Open
        if candle.high < candle.open:
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="high_gte_open",
                    is_valid=False,
                    severity="error",
                    message="High price is less than open price",
                    actual_value=f"high={candle.high}, open={candle.open}",
                    expected_value="high >= open",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="high_gte_open",
                    message="High price is greater than or equal to open price",
                    actual_value=f"high={candle.high}, open={candle.open}",
                )
            )

        # High should be >= Close
        if candle.high < candle.close:
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="high_gte_close",
                    is_valid=False,
                    severity="error",
                    message="High price is less than close price",
                    actual_value=f"high={candle.high}, close={candle.close}",
                    expected_value="high >= close",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="high_gte_close",
                    message="High price is greater than or equal to close price",
                    actual_value=f"high={candle.high}, close={candle.close}",
                )
            )

        # Low should be <= Open
        if candle.low > candle.open:
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="lte_open",
                    is_valid=False,
                    severity="error",
                    message="Low price is greater than open price",
                    actual_value=f"low={candle.low}, open={candle.open}",
                    expected_value="low <= open",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="lte_open",
                    message="Low price is less than or equal to open price",
                    actual_value=f"low={candle.low}, open={candle.open}",
                )
            )

        # Low should be <= Close
        if candle.low > candle.close:
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="lte_close",
                    is_valid=False,
                    severity="error",
                    message="Low price is greater than close price",
                    actual_value=f"low={candle.low}, close={candle.close}",
                    expected_value="low <= close",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="ohlc_logic",
                    validation_rule="lte_close",
                    message="Low price is less than or equal to close price",
                    actual_value=f"low={candle.low}, close={candle.close}",
                )
            )

        return results

    async def _validate_volume_non_negative(
        self, candle: Candle
    ) -> List[ValidationResult]:
        """Validate that volume is non-negative (or null)."""
        results = []

        if candle.volume is not None and candle.volume < 0:
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="volume_validation",
                    validation_rule="volume_non_negative",
                    is_valid=False,
                    severity="error",
                    message="Volume is negative",
                    actual_value=str(candle.volume),
                    expected_value="volume >= 0",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="volume_validation",
                    validation_rule="volume_non_negative",
                    message="Volume is non-negative or null",
                    actual_value=(
                        str(candle.volume) if candle.volume is not None else "null"
                    ),
                )
            )

        return results

    async def _validate_timestamp_sequence(
        self, candle: Candle
    ) -> List[ValidationResult]:
        """Validate that timestamp is reasonable (not too far in past/future)."""
        results = []

        from datetime import datetime, timedelta

        now = (
            datetime.now(candle.timestamp.tzinfo)
            if candle.timestamp.tzinfo
            else datetime.now()
        )

        # Check if timestamp is too far in the future (more than 1 day)
        if candle.timestamp > now + timedelta(days=1):
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="timestamp_validation",
                    validation_rule="timestamp_not_future",
                    is_valid=False,
                    severity="warning",
                    message="Timestamp is more than 1 day in the future",
                    actual_value=str(candle.timestamp),
                    expected_value="timestamp <= now + 1 day",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="timestamp_validation",
                    validation_rule="timestamp_not_future",
                    message="Timestamp is not too far in the future",
                    actual_value=str(candle.timestamp),
                )
            )

        # Check if timestamp is too far in the past (more than 10 years)
        ten_years_ago = now - timedelta(days=365 * 10)
        if candle.timestamp < ten_years_ago:
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="timestamp_validation",
                    validation_rule="timestamp_not_ancient",
                    is_valid=False,
                    severity="warning",
                    message="Timestamp is more than 10 years in the past",
                    actual_value=str(candle.timestamp),
                    expected_value="timestamp >= now - 10 years",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="timestamp_validation",
                    validation_rule="timestamp_not_ancient",
                    message="Timestamp is not too far in the past",
                    actual_value=str(candle.timestamp),
                )
            )

        return results

    async def _validate_price_ranges(self, candle: Candle) -> List[ValidationResult]:
        """Validate that prices are within reasonable ranges."""
        results = []

        # Prices should be positive
        for price_field, price_value in [
            ("open", candle.open),
            ("high", candle.high),
            ("low", candle.low),
            ("close", candle.close),
        ]:
            if price_value <= 0:
                results.append(
                    await self._create_validation_error(
                        candle_id=candle.id,
                        validation_type="price_validation",
                        validation_rule=f"{price_field}_positive",
                        is_valid=False,
                        severity="error",
                        message=f"{price_field.capitalize()} price is not positive",
                        actual_value=str(price_value),
                        expected_value=f"{price_field} > 0",
                    )
                )
            else:
                results.append(
                    await self._create_validation_success(
                        candle_id=candle.id,
                        validation_type="price_validation",
                        validation_rule=f"{price_field}_positive",
                        message=f"{price_field.capitalize()} price is positive",
                        actual_value=str(price_value),
                    )
                )

        return results

    async def _validate_source_and_version(
        self, candle: Candle
    ) -> List[ValidationResult]:
        """Validate that source and dataset version are present."""
        results = []

        # Source should not be empty
        if not candle.source or candle.source.strip() == "":
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="metadata_validation",
                    validation_rule="source_present",
                    is_valid=False,
                    severity="error",
                    message="Source is empty",
                    actual_value=repr(candle.source),
                    expected_value="non-empty string",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="metadata_validation",
                    validation_rule="source_present",
                    message="Source is present",
                    actual_value=candle.source,
                )
            )

        # Dataset version should not be empty
        if not candle.dataset_version or candle.dataset_version.strip() == "":
            results.append(
                await self._create_validation_error(
                    candle_id=candle.id,
                    validation_type="metadata_validation",
                    validation_rule="dataset_version_present",
                    is_valid=False,
                    severity="error",
                    message="Dataset version is empty",
                    actual_value=repr(candle.dataset_version),
                    expected_value="non-empty string",
                )
            )
        else:
            results.append(
                await self._create_validation_success(
                    candle_id=candle.id,
                    validation_type="metadata_validation",
                    validation_rule="dataset_version_present",
                    message="Dataset version is present",
                    actual_value=candle.dataset_version,
                )
            )

        return results

    async def _create_validation_success(
        self,
        candle_id: UUID,
        validation_type: str,
        validation_rule: str,
        message: str,
        actual_value: Optional[str] = None,
        expected_value: Optional[str] = None,
    ) -> ValidationResult:
        """Create a successful validation result."""
        return ValidationResult(
            id=uuid4(),  # We'll set this properly when saving to DB
            candle_id=candle_id,
            validation_type=validation_type,
            validation_rule=validation_rule,
            is_valid=True,
            severity="info",
            message=message,
            actual_value=actual_value,
            expected_value=expected_value,
            validation_metadata={},
        )

    async def _create_validation_error(
        self,
        candle_id: UUID,
        validation_type: str,
        validation_rule: str,
        is_valid: bool,
        severity: str,
        message: str,
        actual_value: Optional[str],
        expected_value: Optional[str],
    ) -> ValidationResult:
        """Create a failed validation result."""
        return ValidationResult(
            id=uuid4(),  # We'll set this properly when saving to DB
            candle_id=candle_id,
            validation_type=validation_type,
            validation_rule=validation_rule,
            is_valid=is_valid,
            severity=severity,
            message=message,
            actual_value=actual_value,
            expected_value=expected_value,
            validation_metadata={},
        )


# Helper function for external use
async def validate_candle_data(
    db: AsyncSession, candle: Candle
) -> List[ValidationResult]:
    """
    Convenience function to validate candle data.

    Args:
        db: Database session
        candle: Candle to validate

    Returns:
        List of validation results
    """
    engine = ValidationEngine(db)
    return await engine.validate_candle(candle)
