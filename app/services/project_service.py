from dotenv import load_dotenv
import os
import random

from storage_service import storage_factory
from annotation_service import annotation_service_factory

class ProjectService:
    def __init__(
            self,
            storage_config: dict,
            annotation_service_config: dict,
            al_batch: int = 2,
        ):
        self.storage = storage_factory(storage_config)
        self.annotation_service = annotation_service_factory(annotation_service_config)
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

if __name__ == "__main__":
    load_dotenv()

    ProjectService(
        storage_config={"images_path": "images"},
        annotation_service_config={
            "url": "http://localhost:8080/",
            "project_id": "1", # unnecessary
            "api_key": os.getenv("API_KEY"),
        }
    ).start_active_learning()