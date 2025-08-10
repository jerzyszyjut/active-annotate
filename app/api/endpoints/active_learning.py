from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.crud.project import ProjectCRUD
from app.crud.annotation_tool_client import AnnotationToolClientCRUD
from app.crud.storage import StorageCRUD
from app.core.config import settings

from app.db.database import get_session

from app.schemas.project import ProjectUpdate
from app.schemas.annotation_tool_client import AnnotationToolClientUpdate
from app.schemas.active_learning import (
    CheckTasksRequest,
    CheckTasksResponse,
    StartActiveLearningResponse,
)

from app.services.project import ProjectService
from app.services.annotation_tool_client import AnnotationToolClientService
from app.services.storage import StorageService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/active-learning", tags=["active-learning"])


@router.post(
    "/start", status_code=status.HTTP_200_OK, response_model=StartActiveLearningResponse
)
async def start_active_learning(
    project_id: int, session: AsyncSession = Depends(get_session)
) -> StartActiveLearningResponse:
    project_crud = ProjectCRUD()
    db_project = await project_crud.get_project_by_id(project_id, session)

    if not db_project.annotation_tool_client_id or not db_project.storage_id:
        raise HTTPException(
            status_code=400,
            detail="Project missing annotation tool client or storage configuration",
        )

    annotation_tool_client_crud = AnnotationToolClientCRUD()
    db_annotation_tool_client = (
        await annotation_tool_client_crud.get_annotation_tool_client_by_id(
            db_project.annotation_tool_client_id, session
        )
    )

    ml_url = f"{settings.ACTIVE_ANNOTATE_HOSTNAME}ml-backend/{project_id}/"

    storage_crud = StorageCRUD()
    db_storage = await storage_crud.get_storage_by_id(db_project.storage_id, session)

    try:
        storage = StorageService(path=db_storage.path)
        annotation_tool_client = AnnotationToolClientService(
            ip_address=db_annotation_tool_client.ip_address,
            port=db_annotation_tool_client.port,
            api_key=db_annotation_tool_client.api_key,
            ml_url=ml_url,
            project_id=db_annotation_tool_client.ls_project_id,  # May be None initially
        )
        project = ProjectService(
            storage,
            annotation_tool_client,
            db_project.name,
            db_project.active_learning_batch_size,
            db_project.label_config,
            db_project.epoch,
        )

        # Create the project and get the Label Studio project ID
        created_project_id = project.create_project_with_initial_batch()

        # Update the annotation tool client with the created project ID
        await annotation_tool_client_crud.update_annotation_tool_client(
            db_annotation_tool_client.id,
            AnnotationToolClientUpdate(ls_project_id=created_project_id),
            session,
        )

        # Update project epoch
        await project_crud.update_project(
            db_project.id, ProjectUpdate(epoch=project.epoch), session
        )

        return StartActiveLearningResponse(
            message="Active learning started successfully",
            project_id=created_project_id,
            images_uploaded=project.al_batch,
            epoch=project.epoch,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start active learning: {str(e)}",
        )


@router.post(
    "/check-tasks", status_code=status.HTTP_200_OK, response_model=CheckTasksResponse
)
async def check_tasks(
    request_data: CheckTasksRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> CheckTasksResponse:
    # Use host from request body if provided, otherwise fallback to request IP
    project_ip_address = request_data.host or (
        request.client.host if request.client else None
    )
    project_data = request_data.project

    logger.info("Received check-tasks request")
    logger.info(f"  Host from body: {request_data.host}")
    logger.info(
        f"  Host from request: {request.client.host if request.client else None}"
    )
    logger.info(f"  Using IP address: {project_ip_address}")
    logger.info(f"  Project data: {project_data.model_dump()}")

    if not project_ip_address:
        raise HTTPException(
            status_code=400,
            detail="Unable to determine host/IP address - please provide 'host' in request body",
        )

    at_client_crud = AnnotationToolClientCRUD()
    db_at_client = await at_client_crud.get_at_client_by_ip_address_and_project_id(
        str(project_ip_address), project_data.id, session
    )

    project_crud = ProjectCRUD()
    db_project = await project_crud.get_project_by_at_client_id(
        db_at_client.id, session
    )

    ml_url = f"{settings.ACTIVE_ANNOTATE_HOSTNAME}ml-backend/{db_project.id}/"

    if project_data.total_annotations_number == db_project.active_learning_batch_size:
        if not db_project.annotation_tool_client_id or not db_project.storage_id:
            raise HTTPException(
                status_code=400,
                detail="Project missing annotation tool client or storage configuration",
            )

        storage_crud = StorageCRUD()
        db_storage = await storage_crud.get_storage_by_id(
            db_project.storage_id, session
        )

        try:
            storage = StorageService(path=db_storage.path)
            annotation_tool_client = AnnotationToolClientService(
                ip_address=db_at_client.ip_address,
                port=db_at_client.port,
                api_key=db_at_client.api_key,
                project_id=db_at_client.ls_project_id,
                ml_url=ml_url,
            )
            project = ProjectService(
                storage,
                annotation_tool_client,
                db_project.name,
                db_project.active_learning_batch_size,
                db_project.label_config,
                db_project.epoch,
            )

            # Start next epoch which creates a new project
            project.start_next_epoch()

            # Update the annotation tool client with the new project ID
            await at_client_crud.update_annotation_tool_client(
                db_at_client.id,
                AnnotationToolClientUpdate(ls_project_id=project.created_project_id),
                session,
            )

            # Update project epoch
            await project_crud.update_project(
                db_project.id, ProjectUpdate(epoch=project.epoch), session
            )

            return CheckTasksResponse(
                message="Next epoch started successfully",
                project_id=project.created_project_id,
                epoch=project.epoch,
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start next epoch: {str(e)}",
            )

    # If batch is not complete, return status without starting new epoch
    return CheckTasksResponse(
        message="Batch not complete yet",
        project_id=None,
        epoch=db_project.epoch,
    )
