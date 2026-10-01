"""Candle CRUD Operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from atra_backend.models.candle import Candle
from atra_backend.api.v1.schemas import CandleCreate, CandleUpdate, MarketDataRequest


async def get_candle(db: AsyncSession, candle_id: UUID) -> Optional[Candle]:
    """Get a candle by ID."""
    result = await db.execute(select(Candle).where(Candle.id == candle_id))
    return result.scalar_one_or_none()


async def get_candles(
    db: AsyncSession,
    asset: str,
    timeframe: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
    offset: int = 0,
) -> List[Candle]:
    """Get candles for asset/timeframe with optional time range."""
    stmt = select(Candle).where(
        and_(
            Candle.asset == asset,
            Candle.timeframe == timeframe,
        )
    )

    if start_time:
        stmt = stmt.where(Candle.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(Candle.timestamp <= end_time)

    stmt = stmt.order_by(desc(Candle.timestamp)).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_latest_candle(
    db: AsyncSession, asset: str, timeframe: str
) -> Optional[Candle]:
    """Get the latest candle for asset/timeframe."""
    stmt = (
        select(Candle)
        .where(and_(Candle.asset == asset, Candle.timeframe == timeframe))
        .order_by(desc(Candle.timestamp))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_candle(db: AsyncSession, candle_in: CandleCreate) -> Candle:
    """Create a new candle."""
    db_candle = Candle(**candle_in.model_dump())
    db.add(db_candle)
    await db.commit()
    await db.refresh(db_candle)
    return db_candle


async def create_candles(
    db: AsyncSession, candles_in: List[CandleCreate]
) -> List[Candle]:
    """Create multiple candles."""
    db_candles = [Candle(**candle.model_dump()) for candle in candles_in]
    db.add_all(db_candles)
    await db.commit()
    for candle in db_candles:
        await db.refresh(candle)
    return db_candles


async def update_candle(
    db: AsyncSession, candle_id: UUID, candle_in: CandleUpdate
) -> Optional[Candle]:
    """Update a candle."""
    db_candle = await get_candle(db, candle_id)
    if not db_candle:
        return None

    update_data = candle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_candle, field, value)

    await db.commit()
    await db.refresh(db_candle)
    return db_candle


async def delete_candle(db: AsyncSession, candle_id: UUID) -> bool:
    """Delete a candle."""
    db_candle = await get_candle(db, candle_id)
    if not db_candle:
        return False

    await db.delete(db_candle)
    await db.commit()
    return True


async def count_candles(
    db: AsyncSession,
    asset: str,
    timeframe: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> int:
    """Count candles for asset/timeframe with optional time range."""
    stmt = select(func.count()).select_from(Candle).where(
        and_(
            Candle.asset == asset,
            Candle.timeframe == timeframe,
        )
    )

    if start_time:
        stmt = stmt.where(Candle.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(Candle.timestamp <= end_time)

    result = await db.execute(stmt)
    return result.scalar_one()