"""Active Learning schemas for request/response models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AnnotationResult(BaseModel):
    """Individual annotation result."""

    value: Dict[str, Any] = Field(..., description="Annotation values")
    id: str = Field(..., description="Result ID")
    from_name: str = Field(..., description="Control tag name")
    to_name: str = Field(..., description="Object tag name")
    type: str = Field(..., description="Result type")
    origin: Optional[str] = Field(None, description="Result origin")


class Annotation(BaseModel):
    """Annotation data from Label Studio webhook."""

    id: int = Field(..., description="Annotation ID")
    result: List[AnnotationResult] = Field(..., description="Annotation results")
    was_cancelled: bool = Field(..., description="Whether annotation was cancelled")
    ground_truth: bool = Field(..., description="Whether annotation is ground truth")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    draft_created_at: Optional[datetime] = Field(
        None, description="Draft creation timestamp"
    )
    lead_time: float = Field(..., description="Time spent on annotation")
    prediction: Dict[str, Any] = Field(..., description="Prediction data")
    result_count: int = Field(..., description="Number of results")
    unique_id: str = Field(..., description="Unique annotation ID")
    import_id: Optional[int] = Field(None, description="Import ID")
    last_action: Optional[str] = Field(None, description="Last action")
    bulk_created: bool = Field(..., description="Whether created in bulk")
    task: int = Field(..., description="Task ID")
    project: int = Field(..., description="Project ID")
    completed_by: int = Field(..., description="User who completed annotation")
    updated_by: int = Field(..., description="User who updated annotation")
    parent_prediction: Optional[int] = Field(None, description="Parent prediction ID")
    parent_annotation: Optional[int] = Field(None, description="Parent annotation ID")
    last_created_by: Optional[int] = Field(None, description="Last creator user ID")


class ProjectData(BaseModel):
    """Detailed project data from Label Studio webhook."""

    id: int = Field(..., description="Label Studio project ID")
    task_number: int = Field(..., description="Total number of tasks")
    finished_task_number: int = Field(..., description="Number of finished tasks")
    total_predictions_number: int = Field(
        ..., description="Total number of predictions"
    )
    total_annotations_number: int = Field(
        ..., description="Total number of annotations"
    )
    num_tasks_with_annotations: int = Field(
        ..., description="Number of tasks with annotations"
    )
    useful_annotation_number: int = Field(
        ..., description="Number of useful annotations"
    )
    ground_truth_number: int = Field(
        ..., description="Number of ground truth annotations"
    )
    skipped_annotations_number: int = Field(
        ..., description="Number of skipped annotations"
    )
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Project description")
    label_config: str = Field(..., description="Label configuration XML")
    parsed_label_config: Dict[str, Any] = Field(
        ..., description="Parsed label configuration"
    )
    label_config_hash: int = Field(..., description="Label configuration hash")
    expert_instruction: str = Field(..., description="Expert instructions")
    show_instruction: bool = Field(..., description="Whether to show instructions")
    show_skip_button: bool = Field(..., description="Whether to show skip button")
    enable_empty_annotation: bool = Field(
        ..., description="Whether to enable empty annotations"
    )
    reveal_preannotations_interactively: bool = Field(
        ..., description="Interactive preannotations"
    )
    show_annotation_history: bool = Field(
        ..., description="Whether to show annotation history"
    )
    show_collab_predictions: bool = Field(
        ..., description="Whether to show collaborative predictions"
    )
    evaluate_predictions_automatically: bool = Field(
        ..., description="Auto-evaluate predictions"
    )
    token: str = Field(..., description="Project token")
    result_count: int = Field(..., description="Result count")
    color: str = Field(..., description="Project color")
    maximum_annotations: int = Field(..., description="Maximum annotations per task")
    min_annotations_to_start_training: int = Field(
        ..., description="Min annotations for training"
    )
    control_weights: Dict[str, Any] = Field(..., description="Control weights")
    model_version: str = Field(..., description="Model version")
    data_types: Dict[str, str] = Field(..., description="Data types mapping")
    is_draft: bool = Field(..., description="Whether project is draft")
    is_published: bool = Field(..., description="Whether project is published")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    sampling: str = Field(..., description="Sampling method")
    skip_queue: str = Field(..., description="Skip queue strategy")
    show_ground_truth_first: bool = Field(..., description="Show ground truth first")
    show_overlap_first: bool = Field(..., description="Show overlap first")
    overlap_cohort_percentage: int = Field(..., description="Overlap cohort percentage")
    task_data_login: Optional[str] = Field(None, description="Task data login")
    task_data_password: Optional[str] = Field(None, description="Task data password")
    pinned_at: Optional[datetime] = Field(None, description="Pinned timestamp")
    custom_task_lock_ttl: Optional[int] = Field(
        None, description="Custom task lock TTL"
    )
    organization: int = Field(..., description="Organization ID")
    created_by: int = Field(..., description="Creator user ID")


class TaskData(BaseModel):
    """Task data from Label Studio webhook."""

    id: int = Field(..., description="Task ID")
    data: Dict[str, Any] = Field(..., description="Task data")
    meta: Dict[str, Any] = Field(..., description="Task metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    is_labeled: bool = Field(..., description="Whether task is labeled")
    overlap: int = Field(..., description="Task overlap")
    inner_id: int = Field(..., description="Internal task ID")
    total_annotations: int = Field(..., description="Total number of annotations")
    cancelled_annotations: int = Field(
        ..., description="Number of cancelled annotations"
    )
    total_predictions: int = Field(..., description="Total number of predictions")
    comment_count: int = Field(..., description="Number of comments")
    unresolved_comment_count: int = Field(
        ..., description="Number of unresolved comments"
    )
    last_comment_updated_at: Optional[datetime] = Field(
        None, description="Last comment update"
    )
    project: int = Field(..., description="Project ID")
    updated_by: int = Field(..., description="User who updated task")
    file_upload: Optional[int] = Field(None, description="File upload ID")
    comment_authors: List[Any] = Field(..., description="Comment authors")


class CheckTasksRequest(BaseModel):
    """Request model for checking tasks and triggering next epoch."""

    action: str = Field(..., description="Action type from webhook")
    annotation: Annotation = Field(..., description="Annotation data")
    project: ProjectData = Field(..., description="Project data from Label Studio")
    task: TaskData = Field(..., description="Task data")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "ANNOTATION_UPDATED",
                "annotation": {
                    "id": 1,
                    "result": [],
                    "was_cancelled": False,
                    "ground_truth": False,
                    "created_at": "2025-08-20T19:51:48.326156Z",
                    "updated_at": "2025-08-20T19:57:59.132896Z",
                    "task": 1,
                    "project": 9,
                },
                "project": {
                    "id": 9,
                    "total_annotations_number": 1,
                    "title": "string_epoch_1",
                },
                "task": {"id": 1, "is_labeled": True, "project": 9},
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
