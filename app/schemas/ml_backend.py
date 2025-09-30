import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, model_validator
from enum import Enum
from typing import Union


logger = logging.getLogger(__name__)


class Task(BaseModel):
    """Represents a single task from Label Studio."""

    id: Optional[int] = None
    data: Dict[str, Any]
    annotations: Optional[List[Dict[str, Any]]] = None
    predictions: Optional[List[Dict[str, Any]]] = None
    meta: Optional[Dict[str, Any]] = None


class PredictionValue(BaseModel):
    """Represents a single prediction value."""

    id: Optional[str] = None
    created_ago: Optional[str] = None
    result: List[Dict[str, Any]]
    score: Optional[float] = None
    cluster: Optional[int] = None
    neighbors: Optional[Dict[str, Any]] = None
    mislabeling: Optional[float] = None
    model_version: Optional[str] = None
    filename: Optional[str] = None

class LSPredictRequest(BaseModel):
    """Request model for /predict endpoint."""

    tasks: List[Task]
    model_version: Optional[str] = None
    project: Optional[str] = None
    label_config: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class PredictResponse(BaseModel):
    """Response model for /predict endpoint."""

    results: List[List[PredictionValue]]


class LSSetupRequest(BaseModel):
    """Request model for /setup endpoint."""

    project: str
    label_config: Optional[str] = None  # Our internal field name
    hostname: Optional[str] = None  # Label Studio sends this
    access_token: Optional[str] = None  # Label Studio sends this
    extra_params: Optional[Dict[str, Any]] = None

    # We need to accept unknown fields like 'schema' that Label Studio sends
    model_config = {"extra": "allow"}

    @model_validator(mode="before")
    @classmethod
    def handle_label_studio_fields(cls, data):
        """Handle Label Studio specific field mappings."""
        logger.info(f"SetupRequest model_validator with data: {data}")

        if isinstance(data, dict):
            # Handle empty string extra_params
            if "extra_params" in data and data["extra_params"] == "":
                data["extra_params"] = {}

            # Map 'schema' to 'label_config' if needed
            if "schema" in data and "label_config" not in data:
                data["label_config"] = data["schema"]
                logger.info(f"Mapped 'schema' to 'label_config': {data['schema']}")

        logger.info(f"Processed data: {data}")
        return data

    def __init__(self, **data):
        logger.info(f"SetupRequest model init with data: {data}")
        try:
            super().__init__(**data)
            logger.info(f"SetupRequest model created successfully: {self}")
        except Exception as e:
            logger.error(f"SetupRequest model validation error: {e}")
            logger.error(f"Error type: {type(e)}")
            raise

    @property
    def get_label_config(self) -> Optional[str]:
        """Get label config."""
        return self.label_config


class TaskType(str, Enum):
    IMAGE_CLASSIFICATION = "IMAGE_CLASSIFICATION"


class MLSetupResponse(BaseModel):
    model_version: str
    task_type: Union[TaskType, str]


class StatusType(str, Enum):
    UP = "UP"
    DOWN = "DOWN"


class MLHealthResponse(BaseModel):
    status: StatusType
    model_class: str


class HealthResponse(BaseModel):
    status: StatusType


class SetupResponse(BaseModel):
    """Response model for /setup endpoint."""

    model_version: Optional[str] = None


class WebhookRequest(BaseModel):
    """Request model for /webhook endpoint."""

    action: str
    project: Dict[str, Any]
    annotation: Optional[Dict[str, Any]] = None
    task: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None


class WebhookResponse(BaseModel):
    """Response model for /webhook endpoint."""

    result: Optional[Any] = None
    status: str = "ok"


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""

    # Define metrics fields as needed
    pass


class TrainRequest(BaseModel):
    """Request model for /train endpoint."""

    project_id: str
    extra_params: Optional[Dict[str, Any]] = None


class TrainResponse(BaseModel):
    """Response model for /train endpoint."""

    status: str = "started"
    message: str = "Training initiated"
    task_id: Optional[str] = None


class ModelResponse(BaseModel):
    """Model response with predictions for Label Studio."""

    model_version: Optional[str] = None
    predictions: List[
        Any
    ]  # Can be List[List[PredictionValue]] or List[PredictionValue]

    def has_model_version(self) -> bool:
        """Check if model version is set."""
        return bool(self.model_version)

    def update_predictions_version(self) -> None:
        """Update model version for all predictions."""
        for prediction in self.predictions:
            if isinstance(prediction, PredictionValue):
                prediction = [prediction]
            if isinstance(prediction, list):
                for p in prediction:
                    if isinstance(p, PredictionValue) and not p.model_version:
                        p.model_version = self.model_version

    def set_version(self, version: str) -> None:
        """Set model version and update all predictions."""
        self.model_version = version
        self.update_predictions_version()
