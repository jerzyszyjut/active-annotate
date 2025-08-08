from label_studio_sdk import LabelStudio
from pathlib import Path


class AnnotationToolClientService:
    def __init__(self, ip_address, port, project_id, api_key):
        self.ip_address = ip_address
        self.port = port
        self.project_id = project_id
        self.api_key = api_key
        self.ls = LabelStudio(
            base_url=f"http://{self.ip_address}:{self.port}", api_key=api_key
        )

    def add_tasks(self, title: str, label_config: str, image_paths: list[Path | str]):
        new_project = self.ls.projects.create(title=title, label_config=label_config)

        if new_project.id is not None:
            self.ls.projects.import_tasks(
                id=new_project.id,
                request=[{"image": image_path} for image_path in image_paths],
            )
            self.project_id = new_project.id
        else:
            raise Exception("Failed to create Label Studio project")
