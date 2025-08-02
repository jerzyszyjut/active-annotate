"""API routes module.

This module contains the main API router configuration.
Additional route modules should be included here as the API grows.
"""

from fastapi import APIRouter
from .endpoints.project import router as project_router
from .endpoints.storage import router as storage_router
from .endpoints.annotation_tool_client import router as atc_router
from .endpoints.active_learning import router as al_router

api_router = APIRouter()

api_router.include_router(project_router)
api_router.include_router(storage_router)
api_router.include_router(atc_router)
api_router.include_router(al_router)
