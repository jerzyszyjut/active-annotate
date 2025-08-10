"""API routes module.

This module contains the main API router configuration.
Additional route modules should be included here as the API grows.
"""

from fastapi import APIRouter
from app.api.endpoints.project import router as project_router
from app.api.endpoints.storage import router as storage_router
from app.api.endpoints.annotation_tool_client import router as atc_router
from app.api.endpoints.active_learning import router as al_router
from app.api.endpoints.ml_backend import router as ml_router

api_router = APIRouter()

api_router.include_router(project_router)
api_router.include_router(storage_router)
api_router.include_router(atc_router)
api_router.include_router(al_router)
api_router.include_router(ml_router)
