from abc import ABC, abstractmethod
from pathlib import Path


class IStorage(ABC):
    @abstractmethod
    def get_image_paths(self) -> list[Path | str]:
        pass

class LocalStorage(IStorage):
    def __init__(self, images_path):
        self.images_path = images_path

    def get_image_paths(self) -> list[Path | str]:
        return [f"/data/local-files/?d={image_path}" for image_path in Path(self.images_path).iterdir()]
    

def storage_factory(config: dict) -> IStorage:
    # storage_type = config["type"]

    return LocalStorage(images_path=config["images_path"])