from label_studio_sdk import LabelStudio
from pathlib import Path


class AnnotationToolClientService:
    def __init__(self, url, project_id, api_key):
        self.url = url
        self.project_id = project_id
        self.api_key = api_key
        self.ls = LabelStudio(
            base_url=url,
            api_key=api_key
        )

    def add_tasks(
            self,
            title: str,
            label_config: str,
            image_paths: list[Path | str]
        ):
    
        new_project = self.ls.projects.create(
            title=title,
            label_config=label_config
        )

        if new_project.id is not None:
            self.ls.projects.import_tasks(
                id=new_project.id,
                request=[{"image": image_path} for image_path in image_paths]
            )
        else:
            raise Exception() 
    