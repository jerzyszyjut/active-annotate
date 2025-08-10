from pathlib import Path
import logging
from typing import List

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self, path: str):
        self.path = Path(path)
        self._validate_path()

    def _validate_path(self) -> None:
        """Validate that the storage path exists and is a directory."""
        if not self.path.exists():
            logger.error(f"Storage path does not exist: {self.path}")
            raise ValueError(f"Storage path does not exist: {self.path}")

        if not self.path.is_dir():
            logger.error(f"Storage path is not a directory: {self.path}")
            raise ValueError(f"Storage path is not a directory: {self.path}")

    def get_image_paths(self) -> List[Path]:
        """Get list of image file paths from the storage directory.

        Returns:
            List of Path objects for image files in the storage directory
        """
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
        image_paths = [
            image_path
            for image_path in self.path.iterdir()
            if image_path.is_file() and image_path.suffix.lower() in image_extensions
        ]

        logger.info(f"Found {len(image_paths)} images in storage path: {self.path}")
        return image_paths

    def get_image_count(self) -> int:
        """Get the count of images in the storage directory.

        Returns:
            Number of image files in the storage directory
        """
        return len(self.get_image_paths())

    def validate_directory(self) -> bool:
        """Validate that the storage directory is accessible and contains images.

        Returns:
            True if directory is valid and contains images, False otherwise
        """
        try:
            self._validate_path()
            image_count = self.get_image_count()
            if image_count == 0:
                logger.warning(f"Storage directory contains no images: {self.path}")
                return False
            return True
        except Exception as e:
            logger.error(f"Storage directory validation failed: {e}")
            return False
