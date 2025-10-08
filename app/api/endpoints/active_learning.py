from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import asyncio

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
from app.services.ml_backend import MLBackendService
from app.services.dataset_converter import DatasetConverterService

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
            label_studio_project_id=db_annotation_tool_client.ls_project_id,  # May be None initially
        )
        project_service = ProjectService(storage, annotation_tool_client, db_project)

        # Create the project and get the Label Studio project ID
        created_project_id = project_service.create_project_with_initial_batch()

        # Update the annotation tool client with the created project ID
        await annotation_tool_client_crud.update_annotation_tool_client(
            db_annotation_tool_client.id,
            AnnotationToolClientUpdate(ls_project_id=created_project_id),
            session,
        )

        # Update project epoch
        await project_crud.update_project(
            db_project.id, ProjectUpdate(epoch=project_service.project.epoch), session
        )

        return StartActiveLearningResponse(
            message="Active learning started successfully",
            project_id=created_project_id,
            images_uploaded=db_project.active_learning_batch_size,
            epoch=project_service.project.epoch,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start active learning: {str(e)}",
        )


@router.post(
    "/check-tasks/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=CheckTasksResponse,
)
async def check_tasks(
    project_id: int,
    request_data: CheckTasksRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> CheckTasksResponse:
    logger.info(
        f"Received webhook for project {project_id}: action={request_data.action}, ls_project_id={request_data.project.id}"
    )

    try:
        # Find our internal project by ID
        project_crud = ProjectCRUD()
        logger.info(f"Looking for project with ID: {project_id}")
        db_project = await project_crud.get_project_by_id(project_id, session)
        logger.info(f"Found project: {db_project.id}")

        # Check if we have reached the target number of annotations for this batch
        if (
            request_data.project.total_annotations_number
            < db_project.active_learning_batch_size
        ):
            return CheckTasksResponse(
                message="Batch not complete yet",
                project_id=None,
                epoch=db_project.epoch,
            )
        
        if not db_project.annotation_tool_client_id or not db_project.storage_id:
            raise HTTPException(
                status_code=400,
                detail="Project missing annotation tool client or storage configuration",
            )

        # Find the annotation tool client associated with this project
        at_client_crud = AnnotationToolClientCRUD()
        logger.info(
            f"Looking for annotation tool client with ID: {db_project.annotation_tool_client_id}"
        )
        db_at_client = await at_client_crud.get_annotation_tool_client_by_id(
            db_project.annotation_tool_client_id, session
        )
        logger.info(f"Found annotation tool client: {db_at_client.id}")

        # Find the storage associated with this project
        storage_crud = StorageCRUD()
        logger.info(
            f"Looking for storage with ID: {db_project.storage_id}"
        )
        db_storage = await storage_crud.get_storage_by_id(
            db_project.storage_id, session
        )
        logger.info(f"Found storage: {db_storage.id}")

        ml_url = f"{settings.ACTIVE_ANNOTATE_HOSTNAME}ml-backend/{db_project.id}/"
        storage = StorageService(path=db_storage.path)
        annotation_tool_client = AnnotationToolClientService(
            ip_address=db_at_client.ip_address,
            port=db_at_client.port,
            api_key=db_at_client.api_key,
            label_studio_project_id=db_at_client.ls_project_id,
            ml_url=ml_url,
            old_ls_projects_id=db_at_client.old_ls_projects_id
        )

        # Export annotations from all annotated projects
        all_annotated_projects_id = db_at_client.old_ls_projects_id.copy()
        all_annotated_projects_id.append(db_at_client.ls_project_id)

        annotations_data = [
            annotation_tool_client.export_annotations(label_studio_project_id=project_id)
            for project_id in all_annotated_projects_id
        ]

        logger.info(
            f"Exporting annotations from projects {all_annotated_projects_id}"
        )


        # Convert annotations to training dataset
        logger.info("Converting annotations to training dataset")
        dataset_converter = DatasetConverterService()
        training_dataset = (
            dataset_converter.convert_ls_annotations_to_training_dataset(
                annotations_data, db_storage.path
            )
        )
        
        if not db_project.ml_backend_url:
            raise HTTPException(
                status_code=400,
                detail="Project missing ml backend configuration",
            )

        # Trigger ML backend training
        logger.info("Starting ML backend training")
        ml_backend = MLBackendService(db_project.ml_backend_url)
        training_response = await ml_backend.train_model(training_dataset)
        logger.info(f"Training initiated: {training_response}")
        
        # Wait for training to complete
        logger.info("Waiting for training to complete...")
        training_complete = False
        max_wait_time = 3600  # 1 hour maximum wait
        check_interval = 30  # Check every 30 seconds
        waited_time = 0

        while not training_complete and waited_time < max_wait_time:
            await asyncio.sleep(check_interval)
            waited_time += check_interval

            try:
                status_response = await ml_backend.get_training_status()
                is_training = status_response.get("is_training", True)

                if not is_training:
                    training_complete = True
                    logger.info("Training completed successfully")
                else:
                    logger.info(
                        f"Training still in progress... (waited {waited_time}s)"
                    )

            except Exception as e:
                logger.warning(f"Failed to check training status: {e}")

        if not training_complete:
            raise HTTPException(
                status_code=408,
                detail="Training did not complete within the expected time",
            )
        
         # Now start next epoch which creates a new project
        logger.info("Training complete, starting next epoch")
        
        project = ProjectService(storage, annotation_tool_client, db_project)

        await project.start_next_epoch()

        # Update the annotation tool client with the new project ID
        await at_client_crud.update_annotation_tool_client(
            db_at_client.id,
            AnnotationToolClientUpdate(
                ls_project_id=project.created_project_id,
                old_ls_projects_id=annotation_tool_client.old_ls_projects_id
            ),
            session,
        )

        # Update project epoch
        await project_crud.update_project(
            db_project.id,
            ProjectUpdate(
                epoch=project.project.epoch,
                annotated_image_paths=project.project.annotated_image_paths
            ),
            session
        )

        if project.running:
            return CheckTasksResponse(
                message="Training completed and next epoch started successfully",
                project_id=project.created_project_id,
                epoch=project.project.epoch,
            )
        else:
            return CheckTasksResponse(
                message="Active learning loop completed successfully. Project object might be used to another project.",
                project_id=0,
                epoch=0
            )

    except HTTPException as e:
        logger.error(f"Database lookup failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during database lookup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )