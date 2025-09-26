import random
import logging

from app.services.annotation_tool_client import AnnotationToolClientService
from app.services.storage import StorageService
from app.schemas.project import ProjectRead

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(
        self,
        storage: StorageService,
        annotation_service_config: AnnotationToolClientService,
        project: ProjectRead,
    ):
        self.storage = storage
        self.annotation_service = annotation_service_config
        self.project = project
        self.created_project_id = None

    def create_project_with_initial_batch(self) -> int:
        """Create a new Label Studio project and upload the first batch of images.

        Returns:
            Created project ID
        """
        try:
            # Validate storage before proceeding
            if not self.storage.validate_directory():
                raise Exception("Storage directory validation failed")

            # Get initial batch of images
            image_paths = self.storage.get_image_paths()
            if not image_paths:
                raise Exception("No images found in storage directory")

            # Select initial batch
            if len(image_paths) >= self.project.active_learning_batch_size:
                selected_paths = random.sample(
                    image_paths, k=self.project.active_learning_batch_size
                )
            else:
                selected_paths = image_paths
                logger.warning(
                    f"Only {len(image_paths)} images available, less than batch size {self.project.active_learning_batch_size}"
                )

            # Create project and upload images
            project_title = f"{self.project.name}_epoch_{self.project.epoch}"
            project_id = self.annotation_service.create_project_and_upload_images(
                title=project_title,
                label_config=self.project.label_config,
                project_id=self.project.id,
                image_paths=selected_paths,
            )

            self.created_project_id = project_id
            logger.info(
                f"Created project '{project_title}' with {len(selected_paths)} images"
            )

            return project_id

        except Exception as e:
            logger.error(f"Failed to create project with initial batch: {e}")
            raise Exception(f"Project creation failed: {e}")

    def start_active_learning(self):
        """Start active learning by creating a project with the first batch."""
        if self.created_project_id is None:
            self.create_project_with_initial_batch()
        else:
            self.start_next_epoch()

    def start_next_epoch(self):
        """Start the next epoch by creating a new project with the next batch."""
        self.epoch += 1
        self.select_batch()

    def select_batch(self):
        """Select and upload the next batch of images to a new project."""
        try:
            image_paths = self.storage.get_image_paths()
            if len(image_paths) >= self.project.active_learning_batch_size:
                selected_paths = random.sample(
                    image_paths, k=self.project.active_learning_batch_size
                )
            else:
                selected_paths = image_paths

            project_title = f"{self.project.name}_epoch_{self.epoch}"
            project_id = self.annotation_service.create_project_and_upload_images(
                title=project_title,
                label_config=self.project.label_config,
                project_id=self.project.id,
                image_paths=selected_paths,
            )

            self.created_project_id = project_id
            logger.info(
                f"Created epoch {self.epoch} project with {len(selected_paths)} images"
            )

        except Exception as e:
            logger.error(f"Failed to select batch for epoch {self.epoch}: {e}")
            raise Exception(f"Batch selection failed: {e}")

    def get_project_info(self) -> dict:
        """Get information about the current project.

        Returns:
            Dictionary with project information
        """
        return {
            "name": self.project.name,
            "epoch": self.epoch,
            "batch_size": self.project.active_learning_batch_size,
            "storage_path": str(self.storage.path),
            "created_project_id": self.created_project_id,
            "total_images": self.storage.get_image_count(),
        }
