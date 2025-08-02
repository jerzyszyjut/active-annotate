from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.project import ProjectCRUD
from app.crud.annotation_tool_client import AnnotationToolClientCRUD
from app.crud.storage import StorageCRUD

from app.db.database import get_session

from app.services.project import ProjectService
from app.services.annotation_tool_client import AnnotationToolClientService
from app.services.storage import StorageService


router = APIRouter(prefix="/active-learning", tags=["active-learning"])


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_active_learning(
    project_id: int,
    session: AsyncSession = Depends(get_session)
):
    project_crud = ProjectCRUD()
    db_project = await project_crud.get_project_by_id(project_id, session)
    
    if not db_project.annotation_tool_client_id or not db_project.storage_id:
        raise Exception() # fix
    
    annotation_tool_client_crud = AnnotationToolClientCRUD()
    db_annotation_tool_client = await annotation_tool_client_crud.get_annotation_tool_client_by_id(db_project.annotation_tool_client_id, session)

    storage_crud = StorageCRUD()
    db_storage = await storage_crud.get_storage_by_id(db_project.storage_id, session)

    storage = StorageService(path=db_storage.path)
    annotation_tool_client = AnnotationToolClientService(
        url=db_annotation_tool_client.url,
        project_id=db_annotation_tool_client.ls_project_id,
        api_key=db_annotation_tool_client.api_key
    )
    ProjectService(storage, annotation_tool_client).start_active_learning()




    

    
    
    