from label_studio_sdk import LabelStudio
from pathlib import Path
from typing import Sequence


class AnnotationToolClientService:
    def __init__(self, ip_address, port, project_id, api_key):
        self.ip_address = ip_address
        self.port = port
        self.project_id = project_id
        self.api_key = api_key
        self.ls = LabelStudio(
            base_url=f"http://{self.ip_address}:{self.port}", api_key=api_key
        )

    def add_tasks(
        self, title: str, label_config: str, image_paths: Sequence[Path | str]
    ):
        new_project = self.ls.projects.create(title=title, label_config=label_config)

        if new_project.id is not None:
            self.ls.projects.import_tasks(
                id=new_project.id,
                request=[{"image": image_path} for image_path in image_paths],
            )
            self.project_id = new_project.id
        else:
            raise Exception("Failed to create Label Studio project")

    def get_annotated_data(self):
        tasks = self.ls.tasks.list(project=self.project_id, fields='all')

        results = {}

        for task in tasks:
            if not task.annotations:
                continue
            
            image_name = task.data.get("image")
            label = task.annotations[0]["result"][0]["value"]["choices"][0]
            
            results[image_name] = label

        return results
        
if __name__ == "__main__":
    atc = AnnotationToolClientService("127.0.0.1", "8080", 19, "")
    atc.get_annotated_data()
