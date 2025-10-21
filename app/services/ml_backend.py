"""ML Backend Service.

This module handles the communication with ML backends and prediction processing
for Label Studio integration.
"""

import base64
import logging
import xml.etree.ElementTree as ET
from io import BytesIO
from operator import itemgetter
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.annotation_tool_client import AnnotationToolClientCRUD
from app.schemas.ml_backend import (
    Task,
    PredictionValue,
    PredictionValues,
    LSPredictRequest,
    PredictResponse,
    ALPredictResponse,
)

logger = logging.getLogger(__name__)


class MLBackendService:
    def __init__(self, ml_backend_url: str):
        self.ml_backend_url = ml_backend_url
        self._cached_label_config = None
        self._cached_choices = None

    def _parse_label_config(self, label_config: Optional[str]) -> Dict[str, Any]:
        if not label_config:
            return {"choices": [], "from_name": "label", "to_name": "image"}

        if self._cached_label_config == label_config and self._cached_choices:
            return self._cached_choices

        try:
            root = ET.fromstring(label_config.strip())

            choices = []
            from_name = "label"  # default
            to_name = "image"  # default

            for choices_elem in root.iter("Choices"):
                from_name = choices_elem.get("name", "label")
                to_name = choices_elem.get("toName", "image")

                for choice_elem in choices_elem.iter("Choice"):
                    value = choice_elem.get("value")
                    if value:
                        choices.append(value)

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
        label_studio_config = None
        if annotation_tool_client_id:
            label_studio_config = await self._get_label_studio_config(
                annotation_tool_client_id, session
            )

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
        task_predictions = []

        try:
            image_bytes, content_type, filename = await self._extract_image_from_task(
                task, label_studio_config
            )

            logger.debug(
                f"Extracted image - content_type: {content_type}, filename: {filename}"
            )

            if not image_bytes:
                logger.warning(f"No image data extracted for task {task.id}")
                return task_predictions

            prediction_result = await self._get_ml_prediction(
                image_bytes, content_type, filename
            )

            if prediction_result:
                formatted_prediction = self._format_prediction_for_label_studio(
                    prediction_result, model_version, label_config_info
                )
                task_predictions.append(formatted_prediction)

        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")

        return task_predictions

    async def _extract_image_from_task(
        self, task: Task, label_studio_config: Optional[dict]
    ) -> Tuple[Optional[bytes], str, str]:
        image_data = task.data.get("image")
        if not image_data:
            logger.warning(f"No image data found in task {task.id}")
            return None, "", ""

        filename = task.data.get("filename", f"task_{task.id}.jpg")

        if image_data.startswith("data:"):
            return await self._decode_base64_image(image_data)
        elif image_data.startswith("http") or image_data.startswith("/data/"):
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
        try:
            if label_studio_config and image_data.startswith("/data/"):
                download_url = f"{label_studio_config['base_url']}{image_data}"
                headers = {"Authorization": f"Token {label_studio_config['api_key']}"}

                async with httpx.AsyncClient() as client:
                    response = await client.get(download_url, headers=headers)
                    response.raise_for_status()
                    image_bytes = response.content
                    content_type = response.headers.get("content-type", "image/jpeg")

                return image_bytes, content_type, filename
            else:
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
        try:
            async with httpx.AsyncClient() as client:
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
        predicted_class_idx = max(enumerate(ml_prediction.get("confidences")), key=itemgetter(1))[0]
        predicted_class = ml_prediction.get("classes")[predicted_class_idx]
        confidence = ml_prediction.get("confidences")[predicted_class_idx]

        if model_version is None:
            model_version = ml_prediction.get("model_version", "1.0.0")

        choices = label_config_info.get("choices", [])
        from_name = label_config_info.get("from_name", "label")
        to_name = label_config_info.get("to_name", "image")

        final_choice = predicted_class
        if predicted_class and choices:
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
            elif predicted_class in choices:
                final_choice = predicted_class
                logger.info(f"  Using direct choice match: {final_choice}")

        prediction_result = {
            "value": {"choices": [final_choice]},
            "from_name": from_name,
            "to_name": to_name,
            "type": "choices",
        }

        return PredictionValue(
            result=[prediction_result], score=confidence, model_version=model_version, filename=ml_prediction["filename"]
        )

    def _format_prediction_for_active_learning(
        self,
        ml_prediction: dict,
        model_version: Optional[str],
        label_config_info: Dict[str, Any],
    ) -> PredictionValues:
        classes = ml_prediction["classes"]
        confidences = ml_prediction["confidences"]

        if model_version is None:
            model_version = ml_prediction.get("model_version", "1.0.0")

        choices = label_config_info.get("choices", [])
        from_name = label_config_info.get("from_name", "label")
        to_name = label_config_info.get("to_name", "image")
        
        final_classes = []
        for _class in classes:
            if _class and choices:
                if isinstance(_class, str) and _class.startswith(
                    "class_"
                ):
                    try:
                        class_index = int(_class.split("_")[1])
                        if 0 <= class_index < len(choices):
                            old_class_name = _class
                            _class = choices[class_index]
                            logger.info(
                                f"  Mapped {old_class_name} to choice: {_class}"
                            )
                    except (ValueError, IndexError):
                        logger.warning(
                            f"Could not parse class index from: {_class}"
                        )
                else:
                    logger.info(f"  Using direct choice match: {_class}")
            final_classes.append(_class)

        prediction_result = {
            "value": {"choices": [final_classes]},
            "from_name": from_name,
            "to_name": to_name,
            "type": "choices",
        }

        return PredictionValues(
            result=prediction_result, scores=confidences, model_version=model_version, filename=ml_prediction["filename"]
        )

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ml_backend_url}health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"ML backend health check failed: {e}")
            raise

    async def setup(self, setup_data: Optional[dict] = None) -> dict:
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

    async def train_model(self, dataset_data: bytes) -> dict:
        """Train the ML model with annotated dataset.

        Args:
            dataset_data: ZIP file containing training dataset

        Returns:
            Training response from ML backend
        """
        try:
            async with httpx.AsyncClient() as client:
                files = {
                    "dataset_file": (
                        "training_dataset.zip",
                        BytesIO(dataset_data),
                        "application/zip",
                    )
                }
                response = await client.post(
                    f"{self.ml_backend_url}train",
                    files=files,
                    timeout=60.0,  # Longer timeout for training initiation
                )
                response.raise_for_status()
                logger.info("ML backend training initiated successfully")
                return response.json()
        except Exception as e:
            logger.error(f"ML backend training failed: {e}")
            raise

    async def get_training_status(self) -> dict:
        """Get the current training status from ML backend.

        Returns:
            Training status information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ml_backend_url}status")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get training status: {e}")
            raise

    async def _process_single_image(
        self,
        image_path: Path,
        model_version: Optional[str],
        label_config_info: Dict[str, Any],
    ) -> PredictionValues:
        formatted_prediction = PredictionValues(result={}, scores=[], filename="")
        try:
            with open(image_path, "rb") as f:
                image = f.read()
                image_bytes = bytes(image)

            prediction_result = await self._get_ml_prediction(
                image_bytes, "", str(image_path)
            )

            if not prediction_result:
                raise Exception(f"Failed processing {image_path} image")
            
            formatted_prediction = self._format_prediction_for_active_learning(
                prediction_result, model_version, label_config_info
            )

            if not formatted_prediction:
                raise Exception(f"Failed processing {image_path} image")
        
        except Exception as e:
            logger.error(f"Error processing {image_path} image")

        return formatted_prediction

    async def predict(
        self,
        image_paths: list[Path],
        label_config: Optional[str],
        model_version: Optional[str],
    ) -> ALPredictResponse:
        label_config_info = self._parse_label_config(label_config)

        results = []

        for image_path in image_paths:
            task_predictions = await self._process_single_image(
                image_path, model_version, label_config_info
            )
            results.append(task_predictions)

        return ALPredictResponse(results=results)
