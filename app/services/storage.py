from pathlib import Path


class StorageService:
    def __init__(self, path):
        self.path = path

    def get_image_paths(self) -> list[Path | str]:
        return [f"/data/local-files/?d={image_path}" for image_path in Path(self.path).iterdir()]