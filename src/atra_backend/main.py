"""ATRA Backend Main Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from atra_backend.core.config import settings
from atra_backend.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Trading Research & Analysis Platform Backend",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to ATRA Backend", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}