"""ATRA Backend API V1 Router."""

from fastapi import APIRouter

from atra_backend.api.v1.endpoints import agents, backtesting, candles, health, ml, validation

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(backtesting.router, prefix="/backtesting", tags=["backtesting"])
api_router.include_router(candles.router, prefix="/market", tags=["market data"])
api_router.include_router(validation.router, prefix="/validation", tags=["validation"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])