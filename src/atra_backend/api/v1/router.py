"""ATRA Backend API V1 Router."""

from fastapi import APIRouter

from atra_backend.api.v1.endpoints import health, ml, backtesting, agents

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(backtesting.router, prefix="/backtesting", tags=["backtesting"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])