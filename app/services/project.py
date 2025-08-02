import random

from .annotation_tool_client import AnnotationToolClientService
from .storage import StorageService


class ProjectService:
    def __init__(
            self,
            storage: StorageService,
            annotation_service_config: AnnotationToolClientService,
            al_batch: int = 2,
        ):
        self.storage = storage
        self.annotation_service = annotation_service_config
        self.al_batch = al_batch
        self.epoch = 0

    def start_active_learning(self):
        self.select_batch()
        self.epoch += 1
        
    def select_batch(self):
    
        image_paths = self.storage.get_image_paths()
        selected_paths = random.sample(image_paths, k=self.al_batch)

        self.annotation_service.add_tasks(
            title="test",
            label_config="""
                <View>
                    <Image name="image" value="$image"/>
                    <RectangleLabels name="label" toName="image">
                        <Label value="Airplane" background="green"/>
                        <Label value="Car" background="blue"/>
                    </RectangleLabels>
                </View>
            """,
            image_paths=selected_paths
        )