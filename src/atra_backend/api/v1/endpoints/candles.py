"""Candle Endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from atra_backend.api.deps import get_db
from atra_backend.api.v1.schemas import (
    Candle,
    CandleCreate,
    CandleList,
    CandleUpdate,
)
from atra_backend.crud.candle_crud import (
    count_candles,
    create_candle,
    create_candles,
    delete_candle,
    get_candle,
    get_candles,
    get_latest_candle,
    update_candle,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("", response_model=CandleList)
async def get_candles_endpoint(
    asset: str = Query(..., max_length=20, description="Asset symbol"),
    timeframe: str = Query(
        ..., max_length=10, description="Timeframe (e.g., 1m, 5m, 1h, 1d)"
    ),
    from_time: Optional[datetime] = Query(None, description="Start time (ISO format)"),
    to_time: Optional[datetime] = Query(None, description="End time (ISO format)"),
    limit: int = Query(
        1000, gt=0, le=10000, description="Maximum number of candles to return"
    ),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get candles for a specific asset and timeframe.

    Returns paginated candle data for the specified asset/timeframe combination.
    """
    # Validate timeframe
    if to_time and from_time and to_time < from_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="to_time must be after from_time",
        )

    # Get candles
    candles = await get_candles(
        db=db,
        asset=asset.upper(),
        timeframe=timeframe,
        start_time=from_time,
        end_time=to_time,
        limit=limit,
        offset=offset,
    )

    # Get total count for pagination
    total = await count_candles(
        db=db,
        asset=asset.upper(),
        timeframe=timeframe,
        start_time=from_time,
        end_time=to_time,
    )

    # Calculate pagination info
    pages = (total + limit - 1) // limit if total > 0 else 0
    page = (offset // limit) + 1 if limit > 0 else 1

    return CandleList(
        items=candles,
        total=total,
        page=page,
        size=len(candles),
        pages=pages,
    )


@router.get("/latest", response_model=Optional[Candle])
async def get_latest_candle_endpoint(
    asset: str = Query(..., max_length=20, description="Asset symbol"),
    timeframe: str = Query(
        ..., max_length=10, description="Timeframe (e.g., 1m, 5m, 1h, 1d)"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest candle for an asset/timeframe."""
    candle = await get_latest_candle(
        db=db,
        asset=asset.upper(),
        timeframe=timeframe,
    )
    return candle


@router.get("/{candle_id}", response_model=Candle)
async def get_candle_endpoint(
    candle_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific candle by ID."""
    candle = await get_candle(db, candle_id)
    if not candle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candle with ID {candle_id} not found",
        )
    return candle


@router.post("", response_model=Candle, status_code=status.HTTP_201_CREATED)
async def create_candle_endpoint(
    candle_in: CandleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new candle."""
    # Validate that asset and timeframe are uppercase
    candle_in.asset = candle_in.asset.upper()
    candle_in.timeframe = candle_in.timeframe

    candle = await create_candle(db=db, candle_in=candle_in)
    return candle


@router.post("/batch", response_model=List[Candle], status_code=status.HTTP_201_CREATED)
async def create_candles_endpoint(
    candles_in: List[CandleCreate],
    db: AsyncSession = Depends(get_db),
):
    """Create multiple candles."""
    # Validate that assets and timeframes are uppercase
    for candle_in in candles_in:
        candle_in.asset = candle_in.asset.upper()
        # Note: timeframe validation could be added here if needed

    candles = await create_candles(db=db, candles_in=candles_in)
    return candles


@router.put("/{candle_id}", response_model=Candle)
async def update_candle_endpoint(
    candle_id: UUID,
    candle_in: CandleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing candle."""
    candle = await update_candle(db=db, candle_id=candle_id, candle_in=candle_in)
    if not candle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candle with ID {candle_id} not found",
        )
    return candle


@router.delete("/{candle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candle_endpoint(
    candle_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a candle."""
    success = await delete_candle(db=db, candle_id=candle_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candle with ID {candle_id} not found",
        )
    return None
