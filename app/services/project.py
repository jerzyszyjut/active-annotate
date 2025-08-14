from app.services.annotation_tool_client import AnnotationToolClientService
from app.services.storage import StorageService
from app.services.active_learning_client import ActiveLearningClientService
from app.services.ml_backend import MlBackendService

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

    def start_active_learning(self):
        self.select_batch()
        self.epoch += 1

    def start_next_epoch(self):
        self.select_batch()
        self.epoch += 1

    def select_batch(self):
        image_paths = self.storage.get_image_paths()
        annotated_data = self.active_learning_client.update_annotation(
            self.annotation_service.get_annotated_data()
        )
        
        self.ml_backend.train(annotated_data)
        predictions = self.ml_backend.predict(
            [path for path in image_paths if path not in annotated_data.keys()]
        )
        print(predictions)
        
        selected_paths = self.active_learning_client.select_images(
            image_paths, predictions, self.al_batch
        )

        self.annotation_service.add_tasks(
            title=f"{self.name}_{self.epoch}",
            label_config=self.label_config,
            image_paths=selected_paths,
        )
