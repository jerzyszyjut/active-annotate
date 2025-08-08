"""Active Annotate API main application module.

This module contains the FastAPI application setup and main endpoint definitions.
The application is configured with CORS middleware and includes health check
and welcome endpoints.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.info("Starting Active Annotate API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)
logger.info("API routes configured")


@app.get("/")
async def root():
    """Welcome endpoint that returns a greeting message."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring the API status."""
    return {"status": "healthy"}
