"""Project API routes.

This module contains all the endpoints for proxying to ml backends in the Active Annotate API.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.project import ProjectCRUD
from app.crud.storage import StorageCRUD
from app.db.database import get_session
from app.schemas.ml_backend import (
    LSPredictRequest,
    PredictResponse,
    LSSetupRequest,
    SetupResponse,
    HealthResponse,
)
from app.services.ml_backend import MLBackendService


router = APIRouter(prefix="/ml-backend", tags=["ml-backend"])
project_crud = ProjectCRUD()
storage_crud = StorageCRUD()


@router.get("/{project_id}/")
@router.get("/{project_id}/health")
async def health(
    project_id: int,
    session: AsyncSession = Depends(get_session),
) -> HealthResponse:
    project = await project_crud.get_project_by_id(project_id, session)

    if not project.ml_backend_url:
        raise HTTPException(
            status_code=400, detail="Project has no ML backend URL configured"
        )

    ml_service = MLBackendService(project.ml_backend_url)
    ml_backend_response = await ml_service.health_check()

    return HealthResponse(status=ml_backend_response.get("status", "DOWN"))


@router.post("/{project_id}/setup")
async def setup(
    project_id: int,
    request: LSSetupRequest,
    session: AsyncSession = Depends(get_session),
) -> SetupResponse:
    project = await project_crud.get_project_by_id(project_id, session)

    if not project.ml_backend_url:
        raise HTTPException(
            status_code=400, detail="Project has no ML backend URL configured"
        )

    ml_service = MLBackendService(project.ml_backend_url)
    ml_backend_response = await ml_service.setup()

    return SetupResponse(model_version=ml_backend_response.get("model_version"))


@router.post("/{project_id}/predict", response_model=PredictResponse)
async def predict(
    project_id: int,
    request: LSPredictRequest,
    session: AsyncSession = Depends(get_session),
):
    """Predict endpoint for Label Studio integration.

    Processes tasks from Label Studio, downloads images using Label Studio SDK,
    sends them to ML backend, and returns predictions in Label Studio format.
    """
    project = await project_crud.get_project_by_id(project_id, session)

    if not project.ml_backend_url:
        raise HTTPException(
            status_code=400, detail="Project has no ML backend URL configured"
        )

    # Ensure label_config is available - use from request or fallback to project config
    if not request.label_config and hasattr(project, "label_config"):
        request.label_config = project.label_config

    # Create ML backend service
    ml_service = MLBackendService(project.ml_backend_url)

    # Process predictions
    return await ml_service.process_predictions(
        request=request,
        annotation_tool_client_id=project.annotation_tool_client_id,
        session=session,
    )
