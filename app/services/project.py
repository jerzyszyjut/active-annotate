import random
import logging
from pathlib import Path

from app.services.annotation_tool_client import AnnotationToolClientService
from app.services.active_learning_client import ActiveLearningClientService
from app.services.storage import StorageService
from app.services.ml_backend import MLBackendService

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
        self.running = False

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

    async def start_active_learning(self):
        """Start active learning by creating a project with the first batch."""
        if self.created_project_id is None:
            self.create_project_with_initial_batch()
        else:
            await self.start_next_epoch()
        self.running = True

    async def start_next_epoch(self):
        """Start the next epoch by creating a new project with the next batch."""
        self.project.epoch += 1
        if self.project.epoch >= self.project.max_epochs:
            finished = True
        else:
            finished = await self.select_batch()
        if finished:
            self.finish_active_learning()

    async def select_batch(self):
        """Select and upload the next batch of images to a new project."""
        try:
            tasks = self.annotation_service.get_project_tasks()

            if not self.project.annotated_image_paths:
                self.project.annotated_image_paths = []

            root_image_path = self.storage.get_root_path()
            self.project.annotated_image_paths += [
                str(root_image_path / task.data["filename"]) for task in tasks
            ]
            logger.info(f"Annotated images: {self.project.annotated_image_paths}")

            image_paths = self.storage.get_image_paths()

            non_annotated_image_paths = [Path(path) for path in image_paths if str(path) not in self.project.annotated_image_paths]

            if len(non_annotated_image_paths) == 0:
                return True

            if not self.project.ml_backend_url:
                raise Exception("ML Backend not assosiated with project.")
            
            ml_backend = MLBackendService(self.project.ml_backend_url)
            predictions = await ml_backend.predict(non_annotated_image_paths, self.project.label_config, None)
            
            active_learning_client = ActiveLearningClientService(self.project.method)
            selected_paths = active_learning_client.select_images(
                predictions=predictions,
                al_batch=self.project.active_learning_batch_size
            )
            logger.info(f"Selected images to annotate: {selected_paths}")

            project_title = f"{self.project.name}_epoch_{self.project.epoch}"
            project_id = self.annotation_service.create_project_and_upload_images(
                title=project_title,
                label_config=self.project.label_config,
                project_id=self.project.id,
                image_paths=selected_paths,
            )

            self.created_project_id = project_id
            logger.info(
                f"Created epoch {self.project.epoch} project with {len(selected_paths)} images"
            )

            return False

        except Exception as e:
            logger.error(f"Failed to select batch for epoch {self.project.epoch}: {e}")
            raise Exception(f"Batch selection failed: {e}")
        
    def finish_active_learning(self):
        try:
            self.annotation_service.delete_webhooks(self.project.id)
            self.created_project_id = 0
            self.project.annotated_image_paths = []
            self.project.epoch = 0
            self.running = False
            logger.info("Active learning loop has finished successfully.")
        except Exception as e:
            logger.error(f"Failed to finish active learning loop: {e}")
            raise Exception(f"Finishing project active learning loop: {e}")

    def get_project_info(self) -> dict:
        """Get information about the current project.

        Returns:
            Dictionary with project information
        """
        return {
            "name": self.project.name,
            "epoch": self.project.epoch,
            "batch_size": self.project.active_learning_batch_size,
            "storage_path": str(self.storage.path),
            "created_project_id": self.created_project_id,
            "total_images": self.storage.get_image_count(),
        }
