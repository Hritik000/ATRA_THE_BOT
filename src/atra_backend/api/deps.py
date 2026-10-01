"""API Dependencies."""

from typing import AsyncGenerator, Optional

from fastapi import Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from atra_backend.core.config import settings

# Engine will be created lazily
_engine: Optional[AsyncEngine] = None
_AsyncSessionLocal: Optional[sessionmaker] = None


def _get_engine():
    """Get or create the async engine."""
    global _engine, _AsyncSessionLocal
    if _engine is None:
        _engine = create_async_engine(
            settings.ASYNC_DATABASE_URL,
            future=True,
        )
        _AsyncSessionLocal = sessionmaker(
            _engine, class_=AsyncSession, expire_on_commit=False
        )
    return _engine


def _get_session_factory():
    """Get or create the async session factory."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _get_engine()  # This will initialize both _engine and _AsyncSessionLocal
    return _AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.

    Yields:
        AsyncSession: Database session
    """
    try:
        AsyncSessionLocal = _get_session_factory()
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    except Exception as e:
        # If there's a database connection error, we still need to yield something
        # but the actual database operations will fail later
        # This allows the application to start even if DB is not available
        raise e


def get_api_key(
    api_key_header: Optional[str] = Header(None, alias=settings.API_KEY_NAME)
) -> Optional[str]:
    """
    Validate API key header if API_KEY is set in settings.

    Returns:
        Optional[str]: The API key if valid, None if API_KEY not configured.
    """
    if settings.API_KEY is None:
        # API key not configured, skip validation
        return None
    if api_key_header == settings.API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )
