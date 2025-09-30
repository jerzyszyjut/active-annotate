from label_studio_sdk import LabelStudio
from pathlib import Path
from typing import Sequence, Optional, Dict, Any
import logging
import base64
import mimetypes
from app.core.config import settings

logger = logging.getLogger(__name__)


class AnnotationToolClientService:
    def __init__(
        self,
        ip_address: str,
        port: int,
        api_key: str,
        ml_url: str,
        label_studio_project_id: Optional[int] = None,
    ):
        self.ip_address = ip_address
        self.port = port
        self.label_studio_project_id = label_studio_project_id
        self.api_key = api_key
        self.ml_url = ml_url
        self.base_url = f"http://{self.ip_address}:{self.port}"
        self.check_tasks_url = (
            f"{settings.ACTIVE_ANNOTATE_HOSTNAME}active-learning/check-tasks"
        )
        self.ls = LabelStudio(base_url=self.base_url, api_key=api_key)

    def create_project_and_upload_images(
        self,
        title: str,
        project_id: int,
        label_config: str,
        image_paths: Sequence[Path],
    ) -> int:
        try:
            project = self.ls.projects.create(title=title, label_config=label_config)

            if not project or not hasattr(project, "id") or project.id is None:
                raise Exception("Failed to create Label Studio project")

            logger.info(f"Created Label Studio project '{title}' with ID: {project.id}")
            self.label_studio_project_id = project.id

            if image_paths:
                self._upload_local_images(project.id, image_paths)

            self.ls.ml.create(project=project.id, url=self.ml_url, is_interactive=True)
            self.ls.webhooks.create(
                project=project.id,
                url=f"{self.check_tasks_url}/{str(project_id)}",
                actions=[
                    "ANNOTATION_CREATED",
                    "ANNOTATION_UPDATED",
                ]
            )

            return project.id

        except Exception as e:
            if self.label_studio_project_id:
                self.ls.projects.delete(self.label_studio_project_id)
            logger.error(f"Failed to create project and upload images: {e}")
            raise Exception(f"Failed to create Label Studio project: {e}")

    def _upload_local_images(
        self, label_studio_project_id: int, image_paths: Sequence[Path]
    ) -> None:
        """Upload local image files to a Label Studio project.

        Args:
            label_studio_project_id: Label Studio project ID
            image_paths: List of local image file paths
        """
        try:
            tasks = []

            for image_path in image_paths:
                if not image_path.exists() or not image_path.is_file():
                    logger.warning(f"Skipping non-existent file: {image_path}")
                    continue

                # Read and encode image file
                try:
                    with open(image_path, "rb") as f:
                        image_data = f.read()

                    # Get MIME type
                    mime_type, _ = mimetypes.guess_type(str(image_path))
                    if mime_type is None:
                        mime_type = "image/jpeg"  # Default fallback

                    # Encode as base64 data URL
                    encoded_image = base64.b64encode(image_data).decode("utf-8")
                    data_url = f"data:{mime_type};base64,{encoded_image}"

                    # Create task data
                    task_data = {"image": data_url, "filename": image_path.name}

                    tasks.append(task_data)
                    logger.debug(f"Prepared task for image: {image_path.name}")

                except Exception as e:
                    logger.error(f"Failed to process image {image_path}: {e}")
                    continue

            if tasks:
                self.ls.projects.import_tasks(id=label_studio_project_id, request=tasks)
                logger.info(
                    f"Successfully uploaded {len(tasks)} images to project {label_studio_project_id}"
                )
            else:
                logger.warning("No valid images found to upload")

        except Exception as e:
            logger.error(
                f"Failed to upload images to project {label_studio_project_id}: {e}"
            )
            raise Exception(f"Failed to upload images: {e}")

    def get_project_tasks(self) -> list[Dict[str, Any]]:
        """Get all tasks from a Label Studio project.

        Args:
            project_id: Project ID (uses instance project_id if not provided)

        Returns:
            List of task dictionaries
        """
        if self.label_studio_project_id is None:
            raise Exception("No project ID specified")

        try:
            tasks = list(self.ls.tasks.list(project=self.label_studio_project_id))
            logger.info(
                f"Retrieved {len(tasks)} tasks from project {self.label_studio_project_id}"
            )
            return tasks
        except Exception as e:
            logger.error(f"Failed to get tasks from project {self.label_studio_project_id}: {e}")
            raise Exception(f"Failed to get project tasks: {e}")

    def export_annotations(
        self, label_studio_project_id: Optional[int] = None, export_format: str = "JSON"
    ) -> bytes:
        """Export annotations from a Label Studio project.

        Args:
            project_id: Project ID (uses instance project_id if not provided)
            export_format: Export format (JSON, COCO, etc.)

        Returns:
            Exported data as bytes
        """
        target_project_id = label_studio_project_id or self.label_studio_project_id
        if target_project_id is None:
            raise Exception("No project ID specified")

        try:
            # Use the Label Studio SDK to export annotations
            # First create an export
            export_request = self.ls.projects.exports.create(
                project_id=target_project_id
            )

            # Wait for export to complete and download
            export_data_iterator = self.ls.projects.exports.download(
                project_id=target_project_id, export_pk=str(export_request.id)
            )

            # Convert iterator to bytes
            export_data = b"".join(export_data_iterator)

            logger.info(
                f"Successfully exported annotations from project {target_project_id} in {export_format} format"
            )
            return export_data
        except Exception as e:
            logger.error(
                f"Failed to export annotations from project {target_project_id}: {e}"
            )
            raise Exception(f"Failed to export annotations: {e}")
