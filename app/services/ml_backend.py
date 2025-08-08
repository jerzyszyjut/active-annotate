"""ML Backend service layer.

This module contains the business logic for ML backend operations,
including communication with custom ML models and Label Studio integration.
"""

import logging
from typing import List, Dict, Any, Optional
import aiohttp
from app.models.ml_backend import (
    Task,
    PredictionValue,
    ModelResponse,
)
from app.services.label_studio import label_studio_service

logger = logging.getLogger(__name__)


class MLBackendService:
    """Service for handling ML backend operations."""

    def __init__(self, ml_backend_url: Optional[str] = None):
        """
        Initialize ML backend service.

        Args:
            ml_backend_url: URL of the custom ML backend server
        """
        from app.core.config import settings

        self.ml_backend_url = ml_backend_url or settings.ML_BACKEND_URL
        self.model_version = "1.0.0"

        # Initialize Label Studio service with settings
        try:
            from label_studio_sdk import Client

            label_studio_service.label_studio_url = settings.LABEL_STUDIO_URL
            label_studio_service.token = settings.LABEL_STUDIO_TOKEN
            label_studio_service.headers = (
                {"Authorization": f"Token {settings.LABEL_STUDIO_TOKEN}"}
                if settings.LABEL_STUDIO_TOKEN
                else {}
            )

            # Reinitialize the Label Studio client with new settings
            if settings.LABEL_STUDIO_TOKEN:
                label_studio_service.client = Client(
                    url=settings.LABEL_STUDIO_URL, api_key=settings.LABEL_STUDIO_TOKEN
                )
            else:
                label_studio_service.client = Client(url=settings.LABEL_STUDIO_URL)
        except Exception as e:
            logger.error(f"Failed to initialize Label Studio client: {e}")
            raise RuntimeError(
                f"Label Studio SDK is required but failed to initialize: {e}"
            )

    async def predict(
        self,
        tasks: List[Task],
        project_id: Optional[str] = None,
        label_config: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ModelResponse:
        """
        Get predictions from the custom ML backend.

        Args:
            tasks: List of tasks to predict
            project_id: Project identifier
            label_config: Label configuration
            context: Additional context
            **kwargs: Additional parameters

        Returns:
            ModelResponse with predictions
        """
        try:
            logger.info(f"Processing {len(tasks)} tasks for ML backend prediction")
            all_predictions = []

            # Process each task individually by uploading the image file
            for i, task in enumerate(tasks):
                try:
                    logger.info(f"Processing task {i + 1}/{len(tasks)}")

                    # Extract image URL from task data
                    task_data = task.data
                    image_url = None

                    # Try different possible keys for image URL
                    for key in ["image", "image_url", "url", "file", "path"]:
                        if key in task_data:
                            image_url = task_data[key]
                            logger.info(f"Found image URL in '{key}': {image_url}")
                            break

                    if not image_url:
                        logger.error(f"No image URL found in task data: {task_data}")
                        all_predictions.append([])
                        continue

                    # Convert relative URL to absolute URL if needed
                    if image_url.startswith("/"):
                        from app.core.config import settings

                        label_studio_url = settings.LABEL_STUDIO_URL.rstrip("/")
                        image_url = f"{label_studio_url}{image_url}"
                        logger.info(f"Converted to absolute URL: {image_url}")

                    # Download image from Label Studio
                    async with aiohttp.ClientSession() as session:
                        # Use authorization headers from label studio service
                        headers = {}
                        if (
                            hasattr(label_studio_service, "headers")
                            and label_studio_service.headers
                        ):
                            headers = label_studio_service.headers

                        async with session.get(image_url, headers=headers) as response:
                            if response.status != 200:
                                logger.error(
                                    f"Failed to download image from {image_url}: {response.status}"
                                )
                                all_predictions.append([])
                                continue

                            image_bytes = await response.read()
                            logger.info(
                                f"Downloaded {len(image_bytes)} bytes from {image_url}"
                            )

                    # Upload image to ML backend for prediction
                    async with aiohttp.ClientSession() as session:
                        # Create form data with the image file
                        form_data = aiohttp.FormData()
                        form_data.add_field(
                            "file",
                            image_bytes,
                            filename=f"task_{i + 1}.jpg",
                            content_type="image/jpeg",
                        )

                        async with session.post(
                            f"{self.ml_backend_url}/predict",
                            data=form_data,
                            timeout=aiohttp.ClientTimeout(total=30),
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                predicted_class = result.get(
                                    "predicted_class", "unknown"
                                )
                                confidence = result.get("confidence", 0.0)
                                logger.info(
                                    f"Prediction for task {i + 1}: {predicted_class} (confidence: {confidence:.3f})"
                                )

                                # Format as Label Studio prediction
                                prediction = PredictionValue(
                                    result=[
                                        {
                                            "from_name": "label",
                                            "to_name": "image",
                                            "type": "choices",
                                            "value": {"choices": [predicted_class]},
                                        }
                                    ],
                                    score=confidence,  # Use actual confidence instead of fixed 0.9
                                    model_version=self.model_version,
                                )
                                all_predictions.append([prediction])
                            else:
                                logger.error(
                                    f"ML backend returned status {response.status} for task {i + 1}"
                                )
                                text = await response.text()
                                logger.error(f"Response: {text}")
                                all_predictions.append([])

                except Exception as task_error:
                    logger.error(f"Error processing task {i + 1}: {task_error}")
                    import traceback

                    traceback.print_exc()
                    all_predictions.append([])

            logger.info(f"Generated predictions for {len(all_predictions)} tasks")

            # Create response with model version
            response = ModelResponse(
                model_version=self.model_version, predictions=all_predictions
            )

            # Ensure model version is set on all predictions
            response.set_version(self.model_version)

            logger.info(f"ModelResponse created with version: {response.model_version}")
            logger.info(f"Response dict: {response.model_dump()}")
            return response

        except Exception as e:
            logger.error(f"Error calling ML backend: {e}")
            import traceback

            traceback.print_exc()
            return self._empty_predictions(tasks)

    async def setup(
        self,
        project_id: str,
        label_config: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Setup ML model for a project.

        Args:
            project_id: Project identifier
            label_config: Label configuration
            extra_params: Additional parameters

        Returns:
            Setup response with model version
        """
        logger.info("=== ML BACKEND SERVICE SETUP CALLED ===")
        logger.info(f"Service setup called with project_id: {project_id}")
        logger.info(f"Service setup called with label_config: {label_config}")
        logger.info(f"Service setup called with extra_params: {extra_params}")
        logger.info(f"ML backend URL: {self.ml_backend_url}")

        try:
            request_data = {
                "project_id": project_id,
                "label_config": label_config or "",
                "extra_params": extra_params or {},
            }
            logger.info(f"Sending request data to ML backend: {request_data}")

            async with aiohttp.ClientSession() as session:
                logger.info(f"Making POST request to: {self.ml_backend_url}/setup")
                async with session.post(
                    f"{self.ml_backend_url}/setup",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    logger.info(f"ML backend response status: {response.status}")
                    response_text = await response.text()
                    logger.info(f"ML backend response text: {response_text}")

                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"ML backend setup success, result: {result}")
                        return {
                            "model_version": result.get(
                                "model_version", self.model_version
                            )
                        }
                    else:
                        logger.error(
                            f"ML backend setup returned status {response.status}"
                        )
                        logger.error(f"Response body: {response_text}")
                        return {"model_version": self.model_version}

        except Exception as e:
            logger.error(f"Error setting up ML backend: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            return {"model_version": self.model_version}

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of the ML backend.

        Returns:
            Health status
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ml_backend_url}/health",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "UP",
                            "ml_backend_status": result.get("status", "UP"),
                            "model_class": result.get("model_class", "CustomMLModel"),
                        }
                    else:
                        return {
                            "status": "DOWN",
                            "ml_backend_status": "DOWN",
                            "error": f"Status code: {response.status}",
                        }

        except Exception as e:
            return {"status": "DOWN", "ml_backend_status": "DOWN", "error": str(e)}

    async def train_model(
        self,
        project_id: str,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Train the ML model with data from Label Studio.

        Args:
            project_id: Label Studio project ID
            label_config: Label configuration
            use_ground_truth: Whether to use ground truth annotations
            extra_params: Additional parameters

        Returns:
            Training response
        """
        try:
            # Prepare dataset from Label Studio
            logger.info(f"Preparing training dataset for project {project_id}")
            dataset_dir = await label_studio_service.prepare_training_dataset(
                project_id
            )

            # Create ZIP file from dataset
            zip_path = await label_studio_service.create_dataset_zip(dataset_dir)

            # Upload dataset to ML backend
            logger.info(f"Uploading dataset to ML backend: {zip_path}")
            async with aiohttp.ClientSession() as session:
                with open(zip_path, "rb") as f:
                    data = aiohttp.FormData()
                    data.add_field(
                        "dataset_file",
                        f,
                        filename=zip_path.name,
                        content_type="application/zip",
                    )
                    data.add_field("project_id", project_id)
                    data.add_field(
                        "project_name", project_id
                    )  # Use project_id as project_name for now
                    if extra_params:
                        for key, value in extra_params.items():
                            data.add_field(key, str(value))

                    logger.info(
                        f"Sending training request to {self.ml_backend_url}/train"
                    )
                    logger.info(
                        f"Form data fields: project_id={project_id}, project_name={project_id}"
                    )

                    async with session.post(
                        f"{self.ml_backend_url}/train",
                        data=data,
                        timeout=aiohttp.ClientTimeout(
                            total=300
                        ),  # 5 minutes for training
                    ) as response:
                        response_text = await response.text()
                        logger.info(f"ML backend response status: {response.status}")
                        logger.info(f"ML backend response text: {response_text}")

                        if response.status == 200:
                            result = await response.json()
                            return {
                                "status": "started",
                                "message": "Training initiated successfully",
                                "task_id": result.get("task_id"),
                                "dataset_path": str(zip_path),
                            }
                        else:
                            logger.error(
                                f"ML backend training failed: {response.status} - {response_text}"
                            )
                            return {
                                "status": "error",
                                "message": f"Training failed: {response_text}",
                            }

        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {"status": "error", "message": str(e)}

    def _format_predictions(
        self, predictions: List[Any]
    ) -> List[List[PredictionValue]]:
        """
        Format predictions from ML backend to Label Studio format.

        Args:
            predictions: Raw predictions from ML backend

        Returns:
            Formatted predictions
        """
        formatted_predictions = []

        for prediction in predictions:
            if isinstance(prediction, dict):
                pred_value = PredictionValue(
                    result=prediction.get("result", []),
                    score=prediction.get("score"),
                    model_version=self.model_version,
                )
                formatted_predictions.append([pred_value])
            elif isinstance(prediction, list):
                pred_list = []
                for pred in prediction:
                    pred_value = PredictionValue(
                        result=pred.get("result", []),
                        score=pred.get("score"),
                        model_version=self.model_version,
                    )
                    pred_list.append(pred_value)
                formatted_predictions.append(pred_list)
            else:
                # Empty prediction
                formatted_predictions.append([])

        return formatted_predictions

    def _empty_predictions(self, tasks: List[Task]) -> ModelResponse:
        """
        Create empty predictions for tasks when ML backend fails.

        Args:
            tasks: List of tasks

        Returns:
            ModelResponse with empty predictions
        """
        empty_predictions = [[] for _ in tasks]
        return ModelResponse(
            model_version=self.model_version, predictions=empty_predictions
        )


# Global ML backend service instance
ml_backend_service = MLBackendService()
