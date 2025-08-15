from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.project import ProjectCRUD
from app.crud.annotation_tool_client import AnnotationToolClientCRUD
from app.crud.storage import StorageCRUD
from app.crud.active_learning_client import ActiveLearningClientCRUD


from app.db.database import get_session

from app.schemas.project import ProjectUpdate
from app.schemas.annotation_tool_client import AnnotationToolClientUpdate
from app.schemas.active_learning_client import ActiveLearningClientUpdate

from app.services.project import ProjectService
from app.services.annotation_tool_client import AnnotationToolClientService
from app.services.storage import StorageService
from app.services.active_learning_client import ActiveLearningClientService
from app.services.ml_backend import MlBackendService


router = APIRouter(prefix="/active-learning", tags=["active-learning"])


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_active_learning(
    project_id: int, session: AsyncSession = Depends(get_session)
):
    project_crud = ProjectCRUD()
    db_project = await project_crud.get_project_by_id(project_id, session)

    if not db_project.annotation_tool_client_id or \
       not db_project.storage_id or \
       not db_project.active_learning_client_id:
        raise HTTPException(
            status_code=400,
            detail="Project missing concluded classes configs",
        )

    annotation_tool_client_crud = AnnotationToolClientCRUD()
    db_annotation_tool_client = (
        await annotation_tool_client_crud.get_annotation_tool_client_by_id(
            db_project.annotation_tool_client_id, session
        )
    )

    storage_crud = StorageCRUD()
    db_storage = await storage_crud.get_storage_by_id(db_project.storage_id, session)

    active_learning_client_crud = ActiveLearningClientCRUD()
    db_active_learning_client = (
        await active_learning_client_crud.get_active_learning_client_by_id(
            db_project.active_learning_client_id, session
        )
    )

    storage = StorageService(path=db_storage.path)
    annotation_tool_client = AnnotationToolClientService(
        ip_address=db_annotation_tool_client.ip_address,
        port=db_annotation_tool_client.port,
        project_id=db_annotation_tool_client.ls_project_id,
        api_key=db_annotation_tool_client.api_key,
    )
    active_learning_client = ActiveLearningClientService(
        annotated_data=db_active_learning_client.data,
    )

    project = ProjectService(
        storage,
        annotation_tool_client,
        active_learning_client,
        MlBackendService(),
        db_project.name,
        db_project.active_learning_batch_size,
        db_project.label_config,
    )
    project.start_active_learning()

    await annotation_tool_client_crud.update_annotation_tool_client(
        db_annotation_tool_client.id,
        AnnotationToolClientUpdate(ls_project_id=annotation_tool_client.project_id),
        session,
    )
    await project_crud.update_project(
        db_project.id, ProjectUpdate(epoch=project.epoch), session
    )
    await active_learning_client_crud.update_active_learning_client(
        db_active_learning_client.id,
        ActiveLearningClientUpdate(data=active_learning_client.annotated_data),
        session,
    )


@router.post("/check-tasks", status_code=status.HTTP_200_OK)
async def check_tasks(request: Request, session: AsyncSession = Depends(get_session)):
    data = await request.json()
    project_ip_address = request.client.host if request.client else None
    project_data = data.get("project")

    at_client_crud = AnnotationToolClientCRUD()
    db_at_client = await at_client_crud.get_at_client_by_ip_address_and_project_id(
        str(project_ip_address), project_data.get("id"), session
    )

    project_crud = ProjectCRUD()
    db_project = await project_crud.get_project_by_at_client_id(
        db_at_client.id, session
    )

    if (
        project_data.get("total_annotations_number")
        == db_project.active_learning_batch_size
    ):
        if not db_project.annotation_tool_client_id or \
           not db_project.storage_id or \
           not db_project.active_learning_client_id:
            raise HTTPException(
                status_code=400,
                detail="Project missing concluded classes configs",
            )

        storage_crud = StorageCRUD()
        db_storage = await storage_crud.get_storage_by_id(
            db_project.storage_id, session
        )

        active_learning_client_crud = ActiveLearningClientCRUD()
        db_active_learning_client = (
            await active_learning_client_crud.get_active_learning_client_by_id(
                db_project.active_learning_client_id, session
            )
        )

        storage = StorageService(path=db_storage.path)
        annotation_tool_client = AnnotationToolClientService(
            ip_address=db_at_client.ip_address,
            port=db_at_client.port,
            project_id=db_at_client.ls_project_id,
            api_key=db_at_client.api_key,
        )
        active_learning_client = ActiveLearningClientService(
            annotated_data=db_active_learning_client.data,
        )

        project = ProjectService(
            storage,
            annotation_tool_client,
            active_learning_client,
            MlBackendService(),
            db_project.name,
            db_project.active_learning_batch_size,
            db_project.label_config,
            db_project.epoch,
        )
        project.start_next_epoch()

        await at_client_crud.update_annotation_tool_client(
            db_at_client.id,
            AnnotationToolClientUpdate(ls_project_id=annotation_tool_client.project_id),
            session,
        )
        await project_crud.update_project(
            db_project.id, ProjectUpdate(epoch=project.epoch), session
        )
        await active_learning_client_crud.update_active_learning_client(
            db_active_learning_client.id,
            ActiveLearningClientUpdate(data=active_learning_client.annotated_data),
            session,
        )
