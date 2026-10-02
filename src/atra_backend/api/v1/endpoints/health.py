"""Health Check Endpoints."""

from atra_backend.core.config import settings
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.LOG_LEVEL,
    }


@router.get("/info")
async def info():
    """Application information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_version": settings.API_V1_STR,
    }
