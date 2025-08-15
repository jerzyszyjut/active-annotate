import random
import logging

from app.services.annotation_tool_client import AnnotationToolClientService
from app.services.storage import StorageService
from app.services.active_learning_client import ActiveLearningClientService
from app.services.ml_backend import MlBackendService

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(
        self,
        storage: StorageService,
        annotation_service_config: AnnotationToolClientService,
        active_learning_client: ActiveLearningClientService,
        ml_backend: MlBackendService,
        name: str,
        al_batch: int,
        label_config: str,
        epoch: int = 0,
    ):
        self.storage = storage
        self.annotation_service = annotation_service_config
        self.active_learning_client = active_learning_client
        self.ml_backend = ml_backend
        self.name = name
        self.al_batch = al_batch
        self.label_config = label_config
        self.epoch = epoch
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
            if len(image_paths) >= self.al_batch:
                selected_paths = random.sample(image_paths, k=self.al_batch)
            else:
                selected_paths = image_paths
                logger.warning(
                    f"Only {len(image_paths)} images available, less than batch size {self.al_batch}"
                )

            # Create project and upload images
            project_title = f"{self.name}_epoch_{self.epoch}"
            project_id = self.annotation_service.create_project_and_upload_images(
                title=project_title,
                label_config=self.label_config,
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
    
            if self.epoch > 0:
                annotated_data = self.active_learning_client.update_annotation(
                    self.annotation_service.get_annotated_data()
                )
                
                self.ml_backend.train(annotated_data)
                
                non_annotated_image_paths = [path for path in image_paths if path not in annotated_data.keys()]
                probabilities = self.ml_backend.predict(
                        non_annotated_image_paths
                    )
                print(probabilities)
                
                selected_paths = self.active_learning_client.select_images(
                    non_annotated_image_paths, probabilities, self.al_batch
                )
            else:
                if len(image_paths) >= self.al_batch:
                    selected_paths = random.sample(image_paths, k=self.al_batch)
                else:
                    selected_paths = image_paths

            project_title = f"{self.name}_epoch_{self.epoch}"
            project_id = self.annotation_service.create_project_and_upload_images(
                title=project_title,
                label_config=self.label_config,
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
            "name": self.name,
            "epoch": self.epoch,
            "batch_size": self.al_batch,
            "storage_path": str(self.storage.path),
            "created_project_id": self.created_project_id,
            "total_images": self.storage.get_image_count(),
        }
