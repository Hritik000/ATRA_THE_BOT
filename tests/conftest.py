"""Pytest configuration and shared fixtures for ATRA test suite."""

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from atra_backend.api.deps import get_db
from atra_backend.main import app


@pytest.fixture(autouse=True)
def mock_db_session():
    """
    Mock database session fixture for isolated unit tests.
    Ensures unit tests don't require an external running PostgreSQL instance.
    """
    session = AsyncMock()
    session.add = MagicMock()
    session.add_all = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one.return_value = 0
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result

    async def mock_refresh(obj):
        if hasattr(obj, "id") and obj.id is None:
            obj.id = uuid.uuid4()
        if hasattr(obj, "created_at") and obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)

    session.refresh.side_effect = mock_refresh

    async def override_get_db() -> AsyncGenerator:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield session
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)
