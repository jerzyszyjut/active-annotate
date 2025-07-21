from fastapi import APIRouter
from app.api.endpoints import projects, datapoints, annotations, models, al_methods, annotation_services

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(datapoints.router, prefix="/datapoints", tags=["datapoints"])
api_router.include_router(annotations.router, prefix="/annotations", tags=["annotations"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(al_methods.router, prefix="/al-methods", tags=["al-methods"])
api_router.include_router(annotation_services.router, prefix="/annotation-services", tags=["annotation-services"])
