from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic import Field


class Value(BaseModel):
    choices: list[str]


class ResultItem(BaseModel):
    value: Value
    id: str
    from_name: str
    to_name: str
    type: str
    origin: str


class Annotation(BaseModel):
    id: int
    result: list[ResultItem]
    was_cancelled: bool
    ground_truth: bool
    created_at: str
    updated_at: str
    draft_created_at: Any
    lead_time: float
    prediction: dict[str, Any]
    result_count: int
    unique_id: str
    import_id: Any
    last_action: Any
    bulk_created: bool
    task: int
    project: int
    completed_by: int
    updated_by: int
    parent_prediction: Any
    parent_annotation: Any
    last_created_by: Any


class Input(BaseModel):
    type: str
    value_type: Any = Field(..., alias="valueType")
    value: str


class Label(BaseModel):
    type: str
    to_name: list[str]
    inputs: list[Input]
    labels: list[str]
    labels_attrs: dict[str, dict[str, str]]


class ParsedLabelConfig(BaseModel):
    label: Label


class Label1(BaseModel):
    overall: float
    type: str
    labels: dict[str, float]


class ControlWeights(BaseModel):
    label: Label1


class DataTypes(BaseModel):
    image: str


class Project(BaseModel):
    id: int
    task_number: int
    finished_task_number: int
    total_predictions_number: int
    total_annotations_number: int
    num_tasks_with_annotations: int
    useful_annotation_number: int
    ground_truth_number: int
    skipped_annotations_number: int
    title: str
    description: str
    label_config: str
    parsed_label_config: ParsedLabelConfig
    label_config_hash: int
    expert_instruction: str
    show_instruction: bool
    show_skip_button: bool
    enable_empty_annotation: bool
    reveal_preannotations_interactively: bool
    show_annotation_history: bool
    show_collab_predictions: bool
    evaluate_predictions_automatically: bool
    token: str
    result_count: int
    color: str
    maximum_annotations: int
    min_annotations_to_start_training: int
    control_weights: ControlWeights
    model_version: str
    data_types: DataTypes
    is_draft: bool
    is_published: bool
    created_at: str
    updated_at: str
    sampling: str
    skip_queue: str
    show_ground_truth_first: bool
    show_overlap_first: bool
    overlap_cohort_percentage: int
    task_data_login: Any
    task_data_password: Any
    pinned_at: Any
    custom_task_lock_ttl: Any
    organization: int
    created_by: int


class Data(BaseModel):
    image: str


class Task(BaseModel):
    id: int
    data: Data
    meta: dict[str, Any]
    created_at: str
    updated_at: str
    is_labeled: bool
    overlap: int
    inner_id: int
    total_annotations: int
    cancelled_annotations: int
    total_predictions: int
    comment_count: int
    unresolved_comment_count: int
    last_comment_updated_at: Any
    project: int
    updated_by: int
    file_upload: Any
    comment_authors: list


class LabelStudioAnnotationWebhookModel(BaseModel):
    action: str
    annotation: Annotation
    project: Project
    task: Task
