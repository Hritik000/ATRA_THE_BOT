"""CRUD operations for validation results."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from atra_backend.models.validation import ValidationResult


async def get_validation_result(
    db: AsyncSession,
    validation_id: UUID
) -> Optional[ValidationResult]:
    """Get a validation result by ID."""
    result = await db.execute(
        select(ValidationResult).where(ValidationResult.id == validation_id)
    )
    return result.scalar_one_or_none()


async def get_validation_results(
    db: AsyncSession,
    candle_id: Optional[UUID] = None,
    batch_id: Optional[str] = None,
    validation_type: Optional[str] = None,
    validation_rule: Optional[str] = None,
    is_valid: Optional[bool] = None,
    severity: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0,
) -> List[ValidationResult]:
    """Get validation results with optional filtering."""
    stmt = select(ValidationResult)

    # Apply filters
    conditions = []
    if candle_id is not None:
        conditions.append(ValidationResult.candle_id == candle_id)
    if batch_id is not None:
        conditions.append(ValidationResult.batch_id == batch_id)
    if validation_type is not None:
        conditions.append(ValidationResult.validation_type == validation_type)
    if validation_rule is not None:
        conditions.append(ValidationResult.validation_rule == validation_rule)
    if is_valid is not None:
        conditions.append(ValidationResult.is_valid == is_valid)
    if severity is not None:
        conditions.append(ValidationResult.severity == severity)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Apply pagination and ordering
    stmt = stmt.order_by(desc(ValidationResult.created_at)).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_validation_results_for_candle(
    db: AsyncSession,
    candle_id: UUID,
    limit: int = 100,
    offset: int = 0,
) -> List[ValidationResult]:
    """Get validation results for a specific candle."""
    return await get_validation_results(
        db=db,
        candle_id=candle_id,
        limit=limit,
        offset=offset
    )


async def create_validation_result(
    db: AsyncSession,
    validation_result: ValidationResult
) -> ValidationResult:
    """Create a new validation result."""
    db.add(validation_result)
    await db.commit()
    await db.refresh(validation_result)
    return validation_result


async def create_validation_results(
    db: AsyncSession,
    validation_results: List[ValidationResult]
) -> List[ValidationResult]:
    """Create multiple validation results."""
    db.add_all(validation_results)
    await db.commit()
    for result in validation_results:
        await db.refresh(result)
    return validation_results


async def delete_validation_result(
    db: AsyncSession,
    validation_id: UUID
) -> bool:
    """Delete a validation result by ID."""
    validation_result = await get_validation_result(db, validation_id)
    if validation_result:
        await db.delete(validation_result)
        await db.commit()
        return True
    return False


async def count_validation_results(
    db: AsyncSession,
    candle_id: Optional[UUID] = None,
    batch_id: Optional[str] = None,
    validation_type: Optional[str] = None,
    validation_rule: Optional[str] = None,
    is_valid: Optional[bool] = None,
    severity: Optional[str] = None,
) -> int:
    """Count validation results with optional filtering."""
    from sqlalchemy import select, func

    stmt = select(func.count()).select_from(ValidationResult)

    # Apply filters
    conditions = []
    if candle_id is not None:
        conditions.append(ValidationResult.candle_id == candle_id)
    if batch_id is not None:
        conditions.append(ValidationResult.batch_id == batch_id)
    if validation_type is not None:
        conditions.append(ValidationResult.validation_type == validation_type)
    if validation_rule is not None:
        conditions.append(ValidationResult.validation_rule == validation_rule)
    if is_valid is not None:
        conditions.append(ValidationResult.is_valid == is_valid)
    if severity is not None:
        conditions.append(ValidationResult.severity == severity)

    if conditions:
        from sqlalchemy import and_
        stmt = stmt.where(and_(*conditions))

    result = await db.execute(stmt)
    return result.scalar() or 0