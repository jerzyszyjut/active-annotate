"""ML Backend Service.

This module handles the communication with ML backends and prediction processing
for Label Studio integration.
"""

import base64
import logging
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import List, Optional, Tuple, Dict, Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.annotation_tool_client import AnnotationToolClientCRUD
from app.schemas.ml_backend import (
    Task,
    PredictionValue,
    LSPredictRequest,
    PredictResponse,
)

logger = logging.getLogger(__name__)


class MLBackendService:
    """Service for handling ML backend operations and predictions."""

    def __init__(self, ml_backend_url: str):
        self.ml_backend_url = ml_backend_url
        self._cached_label_config = None
        self._cached_choices = None

    def _parse_label_config(self, label_config: Optional[str]) -> Dict[str, Any]:
        """Parse Label Studio XML configuration to extract choice values and control names.

        Returns:
            Dict with 'choices' list and 'from_name', 'to_name' values
        """
        if not label_config:
            return {"choices": [], "from_name": "label", "to_name": "image"}

        if self._cached_label_config == label_config and self._cached_choices:
            return self._cached_choices

        try:
            # Parse XML
            root = ET.fromstring(label_config.strip())

            choices = []
            from_name = "label"  # default
            to_name = "image"  # default

            # Find Choices element and extract choice values
            for choices_elem in root.iter("Choices"):
                from_name = choices_elem.get("name", "label")
                to_name = choices_elem.get("toName", "image")

                for choice_elem in choices_elem.iter("Choice"):
                    value = choice_elem.get("value")
                    if value:
                        choices.append(value)

            # Cache the results
            result = {"choices": choices, "from_name": from_name, "to_name": to_name}
            self._cached_label_config = label_config
            self._cached_choices = result

            logger.info(
                f"Parsed label config - choices: {choices}, from_name: {from_name}, to_name: {to_name}"
            )
            return result

        except ET.ParseError as e:
            logger.error(f"Failed to parse label config XML: {e}")
            return {"choices": [], "from_name": "label", "to_name": "image"}
        except Exception as e:
            logger.error(f"Error processing label config: {e}")
            return {"choices": [], "from_name": "label", "to_name": "image"}

    async def process_predictions(
        self,
        request: LSPredictRequest,
        annotation_tool_client_id: Optional[int],
        session: AsyncSession,
    ) -> PredictResponse:
        """Process prediction requests from Label Studio.

        Args:
            request: The prediction request from Label Studio
            annotation_tool_client_id: ID of the annotation tool client
            session: Database session

        Returns:
            Formatted prediction response for Label Studio
        """
        # Get annotation tool client if provided
        label_studio_config = None
        if annotation_tool_client_id:
            label_studio_config = await self._get_label_studio_config(
                annotation_tool_client_id, session
            )

        # Parse label configuration to get choices and field names
        label_config_info = self._parse_label_config(request.label_config)

        results = []

        for task in request.tasks:
            task_predictions = await self._process_single_task(
                task, label_studio_config, request.model_version, label_config_info
            )
            results.append(task_predictions)

        return PredictResponse(results=results)

    async def _get_label_studio_config(
        self, annotation_tool_client_id: int, session: AsyncSession
    ) -> dict:
        """Get Label Studio configuration for authenticated downloads."""
        annotation_tool_client_crud = AnnotationToolClientCRUD()
        db_annotation_tool_client = (
            await annotation_tool_client_crud.get_annotation_tool_client_by_id(
                annotation_tool_client_id, session
            )
        )

        return {
            "base_url": f"http://{db_annotation_tool_client.ip_address}:{db_annotation_tool_client.port}",
            "api_key": db_annotation_tool_client.api_key,
            "project_id": db_annotation_tool_client.ls_project_id,
        }

    async def _process_single_task(
        self,
        task: Task,
        label_studio_config: Optional[dict],
        model_version: Optional[str],
        label_config_info: Dict[str, Any],
    ) -> List[PredictionValue]:
        """Process a single task and return predictions."""
        task_predictions = []

        try:
            # Extract and download image
            image_bytes, content_type, filename = await self._extract_image_from_task(
                task, label_studio_config
            )

            logger.debug(
                f"Extracted image - content_type: {content_type}, filename: {filename}"
            )

            if not image_bytes:
                logger.warning(f"No image data extracted for task {task.id}")
                return task_predictions

            # Get prediction from ML backend
            prediction_result = await self._get_ml_prediction(
                image_bytes, content_type, filename
            )

            if prediction_result:
                # Format prediction for Label Studio
                formatted_prediction = self._format_prediction_for_label_studio(
                    prediction_result, model_version, label_config_info
                )
                task_predictions.append(formatted_prediction)

        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            # Continue with other tasks even if one fails

        return task_predictions

    async def _extract_image_from_task(
        self, task: Task, label_studio_config: Optional[dict]
    ) -> Tuple[Optional[bytes], str, str]:
        """Extract image data from a Label Studio task.

        Returns:
            Tuple of (image_bytes, content_type, filename)
        """
        image_data = task.data.get("image")
        if not image_data:
            logger.warning(f"No image data found in task {task.id}")
            return None, "", ""

        filename = task.data.get("filename", f"task_{task.id}.jpg")

        if image_data.startswith("data:"):
            # Handle base64 data URLs
            return await self._decode_base64_image(image_data)
        elif image_data.startswith("http") or image_data.startswith("/data/"):
            # Handle URLs and Label Studio file paths
            return await self._download_image(image_data, label_studio_config, filename)
        else:
            logger.warning(
                f"Unsupported image data format in task {task.id}: {image_data}"
            )
            return None, "", filename

    async def _decode_base64_image(
        self, image_data: str
    ) -> Tuple[Optional[bytes], str, str]:
        """Decode base64 image data."""
        try:
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            # Extract content type from header
            content_type = header.split(";")[0].split(":")[1]
            return image_bytes, content_type, ""
        except Exception as e:
            logger.error(f"Failed to decode base64 image data: {e}")
            return None, "", ""

    async def _download_image(
        self,
        image_data: str,
        label_studio_config: Optional[dict],
        filename: str,
    ) -> Tuple[Optional[bytes], str, str]:
        """Download image from URL or Label Studio file path."""
        try:
            if label_studio_config and image_data.startswith("/data/"):
                # Label Studio file path - use authenticated download
                download_url = f"{label_studio_config['base_url']}{image_data}"
                headers = {"Authorization": f"Token {label_studio_config['api_key']}"}

                async with httpx.AsyncClient() as client:
                    response = await client.get(download_url, headers=headers)
                    response.raise_for_status()
                    image_bytes = response.content
                    content_type = response.headers.get("content-type", "image/jpeg")

                return image_bytes, content_type, filename
            else:
                # External URL - direct download
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_data)
                    response.raise_for_status()
                    image_bytes = response.content
                    content_type = response.headers.get("content-type", "image/jpeg")

                return image_bytes, content_type, filename

        except Exception as e:
            logger.error(f"Failed to download image from {image_data}: {e}")
            return None, "", filename

    async def _get_ml_prediction(
        self, image_bytes: bytes, content_type: str, filename: str
    ) -> Optional[dict]:
        """Send image to ML backend and get prediction."""
        try:
            logger.info("Sending to ML backend:")
            logger.info(f"  filename: {filename}")
            logger.info(f"  image_bytes length: {len(image_bytes)}")

            # Send to ML backend using proper multipart form data
            async with httpx.AsyncClient() as client:
                # Create proper multipart form data with BytesIO
                files = {
                    "file": (
                        filename or "image.jpg",
                        BytesIO(image_bytes),
                        content_type or "image/jpeg",
                    )
                }

                response = await client.post(
                    f"{self.ml_backend_url}predict", files=files, timeout=30.0
                )

                logger.info(f"ML backend response status: {response.status_code}")
                response.raise_for_status()

                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get prediction from ML backend: {e}")
            logger.error(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Failed to get prediction from ML backend: {e}")
            return None

    def _format_prediction_for_label_studio(
        self,
        ml_prediction: dict,
        model_version: Optional[str],
        label_config_info: Dict[str, Any],
    ) -> PredictionValue:
        """Format ML backend prediction for Label Studio."""
        predicted_class = ml_prediction.get("predicted_class")
        confidence = ml_prediction.get("confidence", 0.0)

        if model_version is None:
            model_version = ml_prediction.get("model_version", "1.0.0")

        choices = label_config_info.get("choices", [])
        from_name = label_config_info.get("from_name", "label")
        to_name = label_config_info.get("to_name", "image")

        final_choice = predicted_class
        if predicted_class and choices:
            # If predicted_class looks like "class_N", try to map it to the actual choice
            if isinstance(predicted_class, str) and predicted_class.startswith(
                "class_"
            ):
                try:
                    class_index = int(predicted_class.split("_")[1])
                    if 0 <= class_index < len(choices):
                        final_choice = choices[class_index]
                        logger.info(
                            f"  Mapped {predicted_class} to choice: {final_choice}"
                        )
                except (ValueError, IndexError):
                    logger.warning(
                        f"Could not parse class index from: {predicted_class}"
                    )
            # If it's already a choice value, use it directly
            elif predicted_class in choices:
                final_choice = predicted_class
                logger.info(f"  Using direct choice match: {final_choice}")

        prediction_result = {
            "value": {"choices": [final_choice]},
            "from_name": from_name,
            "to_name": to_name,
            "type": "choices",
        }

        logger.info(f"  formatted prediction_result: {prediction_result}")
        logger.info(f"  model_version: {model_version}")

        return PredictionValue(
            result=[prediction_result], score=confidence, model_version=model_version
        )

    async def health_check(self) -> dict:
        """Check ML backend health."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ml_backend_url}health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"ML backend health check failed: {e}")
            raise

    async def setup(self, setup_data: Optional[dict] = None) -> dict:
        """Setup ML backend."""
        try:
            async with httpx.AsyncClient() as client:
                if setup_data:
                    response = await client.post(
                        f"{self.ml_backend_url}setup", json=setup_data
                    )
                else:
                    response = await client.post(f"{self.ml_backend_url}setup")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"ML backend setup failed: {e}")
            raise
