"""Label Studio data service for downloading and formatting datasets.

This module handles downloading data from Label Studio and converting it
to ImageFolder format for ML model training.
"""

import asyncio
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
from urllib.parse import urlparse
from label_studio_sdk import Client

logger = logging.getLogger(__name__)


class LabelStudioDataService:
    """Service for handling Label Studio data operations."""

    def __init__(
        self,
        label_studio_url: str = "http://localhost:8080",
        token: Optional[str] = None,
    ):
        """
        Initialize Label Studio data service.

        Args:
            label_studio_url: Base URL of Label Studio instance
            token: Authentication token for Label Studio API
        """
        self.label_studio_url = label_studio_url.rstrip("/")
        self.token = token
        self.headers = {"Authorization": f"Token {token}"} if token else {}
        self.client = None  # Initialize client lazily

    def _get_client(self):
        """Get or initialize the Label Studio client."""
        if self.client is None:
            try:
                if self.token:
                    self.client = Client(url=self.label_studio_url, api_key=self.token)
                else:
                    # For development/testing without authentication
                    self.client = Client(url=self.label_studio_url)
            except Exception as e:
                logger.error(f"Failed to initialize Label Studio SDK client: {e}")
                raise RuntimeError(
                    f"Could not connect to Label Studio at {self.label_studio_url}: {e}"
                )
        return self.client

    async def download_project_data(
        self, project_id: str, export_type: str = "JSON"
    ) -> List[Dict[str, Any]]:
        """
        Download project data from Label Studio using SDK.

        Args:
            project_id: Project ID in Label Studio
            export_type: Export format (JSON, COCO, etc.) - currently not used with SDK

        Returns:
            Project data as list of tasks
        """
        try:
            # Get project
            project = self._get_client().get_project(int(project_id))

            # Export tasks with annotations
            tasks = project.get_tasks()
            logger.info(
                f"Retrieved {len(tasks)} tasks from Label Studio project {project_id}"
            )

            # Convert to the expected format
            task_data = []
            for i, task in enumerate(tasks):
                logger.info(f"Processing task {i}: type={type(task)}, content={task}")

                try:
                    # Handle both object and dictionary formats
                    if hasattr(task, "id"):
                        # Task is an object with attributes
                        task_id = task.id
                        task_data_content = task.data if hasattr(task, "data") else {}
                        logger.info(f"Task {i} is an object with id={task_id}")
                    elif isinstance(task, dict):
                        # Task is a dictionary
                        task_id = task.get("id")
                        task_data_content = task.get("data", {})
                        logger.info(f"Task {i} is a dict with id={task_id}")
                    else:
                        logger.error(
                            f"Task {i} is neither object nor dict: {type(task)}"
                        )
                        continue

                    task_dict = {
                        "id": task_id,
                        "data": task_data_content,
                        "annotations": [],
                    }

                    # Get annotations for this task
                    try:
                        annotations = []
                        if hasattr(task, "get_annotations") and callable(
                            getattr(task, "get_annotations")
                        ):
                            annotations = task.get_annotations()  # type: ignore
                        elif isinstance(task, dict):
                            # Fallback: try to get annotations from the task dict or project
                            annotations = task.get("annotations", [])

                        logger.info(
                            f"Found {len(annotations)} annotations for task {task_id}"
                        )

                        for annotation in annotations:
                            if hasattr(annotation, "id"):
                                # Annotation is an object
                                ann_dict = {
                                    "id": annotation.id,
                                    "result": getattr(annotation, "result", []),
                                    "was_cancelled": getattr(
                                        annotation, "was_cancelled", False
                                    ),
                                    "ground_truth": getattr(
                                        annotation, "ground_truth", False
                                    ),
                                    "created_at": getattr(
                                        annotation, "created_at", None
                                    ),
                                    "updated_at": getattr(
                                        annotation, "updated_at", None
                                    ),
                                }
                            elif isinstance(annotation, dict):
                                # Annotation is a dictionary
                                ann_dict = {
                                    "id": annotation.get("id"),
                                    "result": annotation.get("result", []),
                                    "was_cancelled": annotation.get(
                                        "was_cancelled", False
                                    ),
                                    "ground_truth": annotation.get(
                                        "ground_truth", False
                                    ),
                                    "created_at": annotation.get("created_at", None),
                                    "updated_at": annotation.get("updated_at", None),
                                }
                            else:
                                logger.warning(
                                    f"Skipping annotation of unknown type: {type(annotation)}"
                                )
                                continue

                            task_dict["annotations"].append(ann_dict)

                    except Exception as e:
                        logger.error(
                            f"Error processing annotations for task {task_id}: {e}"
                        )
                        # Continue without annotations

                    task_data.append(task_dict)

                except Exception as e:
                    logger.error(f"Error processing task {i}: {e}")
                    continue

            return task_data

        except Exception as e:
            logger.error(f"Error downloading project data with SDK: {e}")
            raise RuntimeError(
                f"Failed to download data from Label Studio project {project_id}: {e}"
            )

    def get_project_tasks_sync(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get project tasks synchronously using Label Studio SDK.

        Args:
            project_id: Project ID in Label Studio

        Returns:
            List of tasks with annotations
        """
        try:
            # Get project
            project = self._get_client().get_project(int(project_id))

            # Get all tasks with annotations
            tasks = project.get_tasks()
            logger.info(
                f"Retrieved {len(tasks)} tasks from Label Studio project {project_id}"
            )

            task_data = []
            for i, task in enumerate(tasks):
                logger.info(f"Processing task {i}: type={type(task)}, content={task}")

                try:
                    # Handle both object and dictionary formats
                    if hasattr(task, "id"):
                        # Task is an object with attributes
                        task_id = task.id
                        task_data_content = task.data if hasattr(task, "data") else {}
                        logger.info(f"Task {i} is an object with id={task_id}")
                    elif isinstance(task, dict):
                        # Task is a dictionary
                        task_id = task.get("id")
                        task_data_content = task.get("data", {})
                        logger.info(f"Task {i} is a dict with id={task_id}")
                    else:
                        logger.error(
                            f"Task {i} is neither object nor dict: {type(task)}"
                        )
                        continue

                    task_dict = {
                        "id": task_id,
                        "data": task_data_content,
                        "annotations": [],
                    }

                    # Get annotations for this task
                    try:
                        annotations = []
                        if hasattr(task, "get_annotations") and callable(
                            getattr(task, "get_annotations")
                        ):
                            annotations = task.get_annotations()  # type: ignore
                        elif isinstance(task, dict):
                            # Fallback: try to get annotations from the task dict or project
                            annotations = task.get("annotations", [])

                        logger.info(
                            f"Found {len(annotations)} annotations for task {task_id}"
                        )

                        for annotation in annotations:
                            if hasattr(annotation, "id"):
                                # Annotation is an object
                                ann_dict = {
                                    "id": annotation.id,
                                    "result": getattr(annotation, "result", []),
                                    "was_cancelled": getattr(
                                        annotation, "was_cancelled", False
                                    ),
                                    "ground_truth": getattr(
                                        annotation, "ground_truth", False
                                    ),
                                    "created_at": getattr(
                                        annotation, "created_at", None
                                    ),
                                    "updated_at": getattr(
                                        annotation, "updated_at", None
                                    ),
                                }
                            elif isinstance(annotation, dict):
                                # Annotation is a dictionary
                                ann_dict = {
                                    "id": annotation.get("id"),
                                    "result": annotation.get("result", []),
                                    "was_cancelled": annotation.get(
                                        "was_cancelled", False
                                    ),
                                    "ground_truth": annotation.get(
                                        "ground_truth", False
                                    ),
                                    "created_at": annotation.get("created_at", None),
                                    "updated_at": annotation.get("updated_at", None),
                                }
                            else:
                                logger.warning(
                                    f"Skipping annotation of unknown type: {type(annotation)}"
                                )
                                continue

                            task_dict["annotations"].append(ann_dict)

                    except Exception as e:
                        logger.error(
                            f"Error processing annotations for task {task_id}: {e}"
                        )
                        # Continue without annotations

                    task_data.append(task_dict)

                except Exception as e:
                    logger.error(f"Error processing task {i}: {e}")
                    continue

            return task_data

        except Exception as e:
            logger.error(f"Error getting project tasks with SDK: {e}")
            raise RuntimeError(
                f"Failed to get tasks from Label Studio project {project_id}: {e}"
            )

    async def download_image(
        self, image_url: str, session: aiohttp.ClientSession, destination: Path
    ) -> bool:
        """
        Download a single image.

        Args:
            image_url: URL of the image to download (may be relative or absolute)
            session: aiohttp session
            destination: Local file path to save image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert relative URLs to absolute URLs
            if image_url.startswith("/"):
                # Relative URL, prepend Label Studio base URL
                full_url = f"{self.label_studio_url}{image_url}"
            elif image_url.startswith("http"):
                # Already an absolute URL
                full_url = image_url
            else:
                # Relative URL without leading slash
                full_url = f"{self.label_studio_url}/{image_url}"

            logger.info(f"Downloading image from: {full_url}")

            async with session.get(full_url, headers=self.headers) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(destination, "wb") as f:
                        f.write(content)
                    logger.info(f"Successfully downloaded image to: {destination}")
                    return True
                else:
                    logger.warning(
                        f"Failed to download image {full_url}: {response.status}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return False

    def extract_image_classifications(
        self, project_data: List[Dict[str, Any]]
    ) -> List[Tuple[str, str]]:
        """
        Extract image URLs and their classifications from project data.

        Args:
            project_data: List of tasks from Label Studio

        Returns:
            List of (image_url, class_label) tuples
        """
        image_classifications = []

        for i, task in enumerate(project_data):
            logger.info(f"Processing task {i} for image extraction")

            # Get image URL from task data
            image_url = None
            task_data = task.get("data", {})
            logger.info(f"Task data keys: {list(task_data.keys())}")

            # Look for image field (common names: image, img, url, etc.)
            for key in ["image", "img", "url", "data"]:
                if key in task_data:
                    image_url = task_data[key]
                    logger.info(f"Found image URL in field '{key}': {image_url}")
                    break

            if not image_url:
                logger.warning(
                    f"No image URL found in task {i}, task_data: {task_data}"
                )
                continue

            # Get annotations
            annotations = task.get("annotations", [])
            if not annotations:
                logger.warning(f"No annotations found for task {i}")
                continue

            # Use the first annotation (completed one)
            annotation = annotations[0]
            results = annotation.get("result", [])
            logger.info(f"Found {len(results)} annotation results for task {i}")

            for result in results:
                logger.info(f"Processing result: {result}")
                if result.get("type") == "choices":
                    choices = result.get("value", {}).get("choices", [])
                    if choices:
                        class_label = choices[0]  # Take first choice
                        logger.info(
                            f"Found classification: {class_label} for image: {image_url}"
                        )
                        image_classifications.append((image_url, class_label))
                        break

        logger.info(f"Extracted {len(image_classifications)} image classifications")
        return image_classifications

    async def create_imagefolder_dataset(
        self, image_classifications: List[Tuple[str, str]], output_dir: Path
    ) -> Path:
        """
        Create ImageFolder format dataset from image classifications.

        Args:
            image_classifications: List of (image_url, class_label) tuples
            output_dir: Directory to create dataset in

        Returns:
            Path to created dataset directory
        """
        # Create class directories
        class_dirs = {}
        for _, class_label in image_classifications:
            class_dir = output_dir / class_label
            class_dir.mkdir(parents=True, exist_ok=True)
            class_dirs[class_label] = class_dir

        # Download images into class directories
        async with aiohttp.ClientSession(headers=self.headers) as session:
            download_tasks = []

            for i, (image_url, class_label) in enumerate(image_classifications):
                # Get file extension from URL
                parsed_url = urlparse(image_url)
                file_ext = Path(parsed_url.path).suffix or ".jpg"

                # Create unique filename
                filename = f"image_{i:05d}{file_ext}"
                destination = class_dirs[class_label] / filename

                # Create download task
                task = self.download_image(image_url, session, destination)
                download_tasks.append(task)

            # Execute downloads concurrently
            if download_tasks:
                results = await asyncio.gather(*download_tasks, return_exceptions=True)
                successful_downloads = sum(1 for result in results if result is True)
                logger.info(
                    f"Downloaded {successful_downloads}/{len(download_tasks)} images"
                )

        return output_dir

    async def prepare_training_dataset(self, project_id: str) -> Path:
        """
        Prepare complete training dataset from Label Studio project.

        Args:
            project_id: Label Studio project ID

        Returns:
            Path to prepared dataset directory
        """
        try:
            # Download project data
            logger.info(f"Downloading data for project {project_id}")

            # Use Label Studio SDK to get project data
            project_data = self.get_project_tasks_sync(project_id)
            logger.info(f"Downloaded {len(project_data)} tasks using Label Studio SDK")

            if not project_data:
                raise ValueError("No project data downloaded")

            # Extract image classifications
            image_classifications = self.extract_image_classifications(project_data)
            logger.info(f"Found {len(image_classifications)} labeled images")

            if not image_classifications:
                raise ValueError("No labeled images found in project")

            # Create temporary directory for dataset
            temp_dir = Path(tempfile.mkdtemp(prefix=f"ls_dataset_{project_id}_"))
            dataset_dir = temp_dir / "dataset"

            # Create ImageFolder format dataset
            logger.info(f"Creating ImageFolder dataset in {dataset_dir}")
            await self.create_imagefolder_dataset(image_classifications, dataset_dir)

            return dataset_dir

        except Exception as e:
            logger.error(f"Error preparing training dataset: {e}")
            raise

    async def create_dataset_zip(self, dataset_dir: Path) -> Path:
        """
        Create a ZIP file from the dataset directory.

        Args:
            dataset_dir: Path to dataset directory

        Returns:
            Path to created ZIP file
        """
        zip_path = dataset_dir.parent / f"{dataset_dir.name}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in dataset_dir.rglob("*"):
                if file_path.is_file():
                    # Create relative path for archive
                    arcname = file_path.relative_to(dataset_dir)
                    zipf.write(file_path, arcname)

        logger.info(f"Created dataset ZIP: {zip_path}")
        return zip_path


# Global service instance
label_studio_service = LabelStudioDataService()
