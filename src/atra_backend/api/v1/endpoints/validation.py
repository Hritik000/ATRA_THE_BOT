"""Validation API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from atra_backend.api.deps import get_db
from atra_backend.crud import candle_crud, validation_crud
from atra_backend.models.validation import ValidationResult
from atra_backend.validation.engine import validate_candle_data
from atra_backend.api.v1.schemas import (
    ValidationResult,
    ValidationResultList,
    ValidationResultCreate,
    ValidationRequest,
)

router = APIRouter()


@router.get("", response_model=ValidationResultList)
async def get_validation_results_endpoint(
    candle_id: Optional[UUID] = Query(None, description="Filter by candle ID"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    validation_type: Optional[str] = Query(None, description="Filter by validation type"),
    validation_rule: Optional[str] = Query(None, description="Filter by validation rule"),
    is_valid: Optional[bool] = Query(None, description="Filter by validation result"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(1000, gt=0, le=10000, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get validation results with optional filtering.
    """
    validation_results = await validation_crud.get_validation_results(
        db=db,
        candle_id=candle_id,
        batch_id=batch_id,
        validation_type=validation_type,
        validation_rule=validation_rule,
        is_valid=is_valid,
        severity=severity,
        limit=limit,
        offset=offset,
    )

    total = await validation_crud.count_validation_results(
        db=db,
        candle_id=candle_id,
        batch_id=batch_id,
        validation_type=validation_type,
        validation_rule=validation_rule,
        is_valid=is_valid,
        severity=severity,
    )

    page = (offset // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1

    return ValidationResultList(
        items=validation_results,
        total=total,
        page=page,
        size=limit,
        pages=pages,
    )


@router.get("/{validation_id}", response_model=ValidationResult)
async def get_validation_result_endpoint(
    validation_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific validation result by ID.
    """
    validation_result = await validation_crud.get_validation_result(db, validation_id)
    if validation_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation result not found",
        )
    return validation_result


@router.get("/candle/{candle_id}", response_model=ValidationResultList)
async def get_validation_results_for_candle_endpoint(
    candle_id: UUID,
    limit: int = Query(1000, gt=0, le=10000, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get validation results for a specific candle.
    """
    # Check if candle exists
    candle = await candle_crud.get_candle(db, candle_id)
    if candle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candle not found",
        )

    validation_results = await validation_crud.get_validation_results_for_candle(
        db=db,
        candle_id=candle_id,
        limit=limit,
        offset=offset,
    )

    total = await validation_crud.count_validation_results(
        db=db,
        candle_id=candle_id,
    )

    page = (offset // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1

    return ValidationResultList(
        items=validation_results,
        total=total,
        page=page,
        size=limit,
        pages=pages,
    )


@router.post("/run", response_model=ValidationResultList)
async def run_validation_endpoint(
    validation_request: ValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run validation on specified candles or all recent candles.
    """
    # Determine which candles to validate
    if validation_request.candle_ids:
        # Validate specific candles
        candles = []
        for candle_id in validation_request.candle_ids:
            candle = await candle_crud.get_candle(db, candle_id)
            if candle is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Candle with ID {candle_id} not found",
                )
            candles.append(candle)
    else:
        # Validate recent candles (default: last 100)
        from datetime import datetime, timedelta

        # Get candles from the last 24 hours by default
        start_time = datetime.now() - timedelta(hours=24)

        # If specific asset/timeframe requested, use those
        # For now, we'll get all recent candles - in practice this might need refinement
        candles = await candle_crud.get_candles(
            db=db,
            asset="",  # Empty string gets all assets (we'll need to adjust this)
            timeframe="",  # Empty string gets all timeframes
            start_time=start_time,
            limit=1000,  # Reasonable limit
        )

        # Filter by asset/timeframe if specified in request
        # This is a simplified approach - in reality we'd want better filtering
        if validation_request.validation_types or validation_request.rules:
            # We'll apply rule filtering in the validation engine
            pass

    if not candles:
        return ValidationResultList(
            items=[],
            total=0,
            page=1,
            size=0,
            pages=0,
        )

    # Run validation on all candles
    all_validation_results = []

    for candle in candles:
        # Run validation
        validation_results = await validate_candle_data(db, candle)

        # Apply filtering if requested
        if validation_request.validation_types or validation_request.rules:
            filtered_results = []
            for result in validation_results:
                type_match = not validation_request.validation_types or result.validation_type in validation_request.validation_types
                rule_match = not validation_request.rules or result.validation_rule in validation_request.rules
                if type_match and rule_match:
                    filtered_results.append(result)
            validation_results = filtered_results

        # Set batch_id if provided
        if validation_request.batch_id:
            for result in validation_results:
                result.batch_id = validation_request.batch_id

        # Save validation results to database
        saved_results = await validation_crud.create_validation_results(db, validation_results)
        all_validation_results.extend(saved_results)

    # Return results
    total = len(all_validation_results)
    page = 1
    size = len(all_validation_results)
    pages = 1 if size > 0 else 0

    return ValidationResultList(
        items=all_validation_results,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=ValidationResult, status_code=status.HTTP_201_CREATED)
async def create_validation_result_endpoint(
    validation_result: ValidationResultCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new validation result (manual creation).
    """
    # If candle_id is provided, verify the candle exists
    if validation_result.candle_id:
        candle = await candle_crud.get_candle(db, validation_result.candle_id)
        if candle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candle not found",
            )

    # Create validation result object
    db_validation_result = ValidationResult(
        **validation_result.dict(exclude_unset=True)
    )

    # Save to database
    saved_result = await validation_crud.create_validation_result(db, db_validation_result)
    return saved_result