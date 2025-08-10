from pathlib import Path


class StorageService:
    def __init__(self, path):
        self.path = path

    def get_image_paths(self) -> list[str]:
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        return [
            f"/data/local-files/?d={image_path}"
            for image_path in Path(self.path).iterdir()
            if image_path.is_file() and image_path.suffix.lower() in image_extensions
        ]
