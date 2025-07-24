"""API routes module.

This module contains the main API router configuration.
Additional route modules should be included here as the API grows.
"""

from fastapi import APIRouter
from app.api.endpoints.project import router as project_router

api_router = APIRouter()

api_router.include_router(project_router)
