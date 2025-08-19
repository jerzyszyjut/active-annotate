"""Active Learning schemas for request/response models."""

from typing import Optional
from pydantic import BaseModel, Field


class ProjectStatusData(BaseModel):
    """Project status data from Label Studio webhook."""

    id: int = Field(..., description="Label Studio project ID")
    total_annotations_number: int = Field(
        ..., description="Total number of annotations in the project"
    )
    title: Optional[str] = Field(None, description="Project title")
    created_by: Optional[dict] = Field(None, description="User who created the project")


class CheckTasksRequest(BaseModel):
    """Request model for checking tasks and triggering next epoch."""

    project: ProjectStatusData = Field(
        ..., description="Project status information from Label Studio"
    )
    action: Optional[str] = Field(None, description="Action type from webhook")
    host: Optional[str] = Field(
        None,
        description="Host/IP address of the Label Studio instance (optional, will fallback to request IP)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "project": {
                    "id": 1,
                    "total_annotations_number": 10,
                    "title": "My Classification Project",
                },
                "action": "ANNOTATION_CREATED",
                "host": "192.168.1.100",
            }
        }


class CheckTasksResponse(BaseModel):
    """Response model for check tasks endpoint."""

    message: str = Field(..., description="Status message")
    project_id: Optional[int] = Field(
        None, description="New project ID if epoch was started"
    )
    epoch: Optional[int] = Field(None, description="Current epoch number")


class StartActiveLearningResponse(BaseModel):
    """Response model for starting active learning."""

    message: str = Field(..., description="Status message")
    project_id: int = Field(..., description="Created Label Studio project ID")
    images_uploaded: int = Field(
        ..., description="Number of images uploaded in initial batch"
    )
    epoch: int = Field(..., description="Current epoch number")
