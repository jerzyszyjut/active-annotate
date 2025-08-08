"""ML Backend API endpoints.

This module contains FastAPI endpoints that implement the Label Studio ML Backend API
for integration with Label Studio and custom ML models.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from app.models.ml_backend import (
    PredictRequest,
    PredictResponse,
    SetupRequest,
    SetupResponse,
    TrainRequest,
    TrainResponse,
    HealthResponse,
    MetricsResponse,
    PredictionValue,
)
from app.services.ml_backend import ml_backend_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ml-backend"])


@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    """
    Get predictions from the ML model.

    This endpoint implements the Label Studio ML Backend /predict API.
    It receives tasks from Label Studio and returns predictions.

    Args:
        request: Prediction request containing tasks and metadata

    Returns:
        Predictions in Label Studio format
    """
    try:
        # Extract project ID from project string (format: "project_id.timestamp")
        project_id = None
        if request.project:
            project_id = request.project.split(".", 1)[0]

        # Get context from params
        context = {}
        if request.params:
            context = request.params.pop("context", {})

        # Call ML backend service
        model_response = await ml_backend_service.predict(
            tasks=request.tasks,
            project_id=project_id,
            label_config=request.label_config,
            context=context,
            **(request.params or {}),
        )

        # Format response for Label Studio
        results = []
        for prediction in model_response.predictions:
            if isinstance(prediction, list):
                # Convert PredictionValue objects to dicts
                prediction_dicts = []
                for pred in prediction:
                    if isinstance(pred, PredictionValue):
                        prediction_dicts.append(pred.model_dump())
                    else:
                        prediction_dicts.append(pred)
                results.append(prediction_dicts)
            else:
                if isinstance(prediction, PredictionValue):
                    results.append([prediction.model_dump()])
                else:
                    results.append([prediction])

        return PredictResponse(results=results)

    except Exception as e:
        logger.error(f"Error in predict endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.post("/setup", response_model=SetupResponse)
async def setup(request: SetupRequest) -> SetupResponse:
    """
    Setup ML model for a project.

    This endpoint implements the Label Studio ML Backend /setup API.
    It initializes the ML model with project configuration.

    Args:
        request: Setup request containing project configuration

    Returns:
        Setup response with model version
    """
    logger.info("=== ML SETUP ENDPOINT CALLED ===")
    logger.info(f"Request data: {request}")
    logger.info(f"Request.project: {request.project}")
    logger.info(f"Request.label_config: {request.label_config}")
    logger.info(f"Request.extra_params: {request.extra_params}")

    try:
        # Extract project ID from project string
        project_id = request.project.split(".", 1)[0] if request.project else None
        logger.info(f"Extracted project_id: {project_id}")

        if not project_id:
            logger.error("Project ID is missing from request")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Project ID is required"
            )

        # Call ML backend service
        logger.info(f"Calling ml_backend_service.setup with project_id={project_id}")
        setup_result = await ml_backend_service.setup(
            project_id=project_id,
            label_config=request.get_label_config,
            extra_params=request.extra_params,
        )
        logger.info(f"ML backend service setup result: {setup_result}")

        response = SetupResponse(model_version=setup_result.get("model_version"))
        logger.info(f"Returning setup response: {response}")
        return response

    except HTTPException as he:
        logger.error(f"HTTP Exception in setup endpoint: {he}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in setup endpoint: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error args: {e.args}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Setup failed: {str(e)}",
        )


@router.post("/train", response_model=TrainResponse)
async def train(request: TrainRequest) -> TrainResponse:
    """
    Train the ML model with data from Label Studio.

    This endpoint downloads data from Label Studio, formats it as ImageFolder,
    and sends it to the custom ML backend for training.

    Args:
        request: Training request containing project configuration

    Returns:
        Training response with status and task ID
    """
    try:
        # Call ML backend service for training
        training_result = await ml_backend_service.train_model(
            project_id=request.project_id,
            extra_params=request.extra_params,
        )

        return TrainResponse(
            status=training_result.get("status", "error"),
            message=training_result.get("message", "Training failed"),
            task_id=training_result.get("task_id"),
        )

    except Exception as e:
        logger.error(f"Error in train endpoint: {e}")
        return TrainResponse(status="error", message=f"Training failed: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Health check endpoint.

    This endpoint implements the Label Studio ML Backend /health API.
    It checks the health of both this service and the connected ML backend.

    Returns:
        Health status
    """
    try:
        # Check ML backend health
        health_status = await ml_backend_service.health_check()

        return HealthResponse(
            status=health_status.get("status", "UP"),
            model_class=health_status.get("model_class"),
        )

    except Exception as e:
        logger.error(f"Error in health endpoint: {e}")
        return HealthResponse(status="DOWN", model_class="Unknown")


@router.get("/metrics", response_model=MetricsResponse)
async def metrics() -> MetricsResponse:
    """
    Get model metrics.

    This endpoint implements the Label Studio ML Backend /metrics API.
    It returns metrics about the ML model performance.

    Returns:
        Model metrics
    """
    try:
        # For now, return empty metrics
        # This can be extended to include actual metrics from the ML backend
        return MetricsResponse()

    except Exception as e:
        logger.error(f"Error in metrics endpoint: {e}")
        return MetricsResponse()


@router.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint that redirects to health check.

    Returns:
        Basic status information
    """
    health_status = await ml_backend_service.health_check()
    return {
        "message": "Active Annotate ML Backend API",
        "status": health_status.get("status", "UP"),
        "endpoints": [
            "/ml/predict",
            "/ml/setup",
            "/ml/train",
            "/ml/health",
            "/ml/metrics",
        ],
    }
