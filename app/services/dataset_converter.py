"""Dataset Converter Service.

This module handles converting Label Studio annotations to training dataset formats.
"""

import json
import logging
import tempfile
import zipfile
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DatasetConverterService:
    """Service for converting Label Studio annotations to training datasets."""

    def __init__(self):
        pass

    def convert_ls_annotations_to_training_dataset(
        self, all_annotations_data: list[bytes], storage_path: str
    ) -> bytes:
        """Convert Label Studio annotations to a training dataset ZIP file.

        Args:
            annotations_data: JSON export data from Label Studio
            storage_path: Path to the storage containing original images

        Returns:
            ZIP file containing organized training dataset as bytes
        """
        try:
            # Parse the annotations JSON
            annotations_json = []
            for annotations_data in all_annotations_data:
                json_data = json.loads(annotations_data.decode("utf-8"))
                annotations_json += json_data
            
            logger.info(
                f"Loaded {len(annotations_json)} annotations for training dataset"
            )

            # Create temporary directory for dataset organization
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                dataset_dir = temp_path / "training_dataset"
                dataset_dir.mkdir(exist_ok=True)

                # Organize images by class
                class_counts = self._organize_images_by_class(
                    annotations_json, storage_path, dataset_dir
                )

                logger.info(f"Organized training dataset with classes: {class_counts}")

                # Validate that we have at least one class with images
                if not class_counts:
                    raise Exception(
                        "No valid annotations found - cannot create training dataset"
                    )

                total_images = sum(class_counts.values())
                if total_images == 0:
                    raise Exception(
                        "No images were successfully organized - cannot create training dataset"
                    )

                logger.info(
                    f"Training dataset ready: {len(class_counts)} classes, {total_images} total images"
                )

                # Create ZIP file in PyTorch ImageFolder format
                # Structure: training_dataset/class_name/image_files
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    # Add all files maintaining the ImageFolder structure
                    for class_dir in dataset_dir.iterdir():
                        if class_dir.is_dir():
                            class_name = class_dir.name
                            for image_file in class_dir.iterdir():
                                if image_file.is_file():
                                    # Create archive path: class_name/image_file.jpg
                                    archive_path = f"{class_name}/{image_file.name}"
                                    zip_file.write(image_file, archive_path)
                                    logger.debug(f"Added to ZIP: {archive_path}")

                # Validate ZIP structure
                self._validate_pytorch_imagefolder_format(zip_buffer)

                zip_buffer.seek(0)
                zip_data = zip_buffer.getvalue()

                logger.info(f"Created training dataset ZIP with {len(zip_data)} bytes")
                return zip_data

        except Exception as e:
            logger.error(f"Failed to convert annotations to training dataset: {e}")
            raise Exception(f"Dataset conversion failed: {e}")

    def _organize_images_by_class(
        self, annotations: List[Dict[str, Any]], storage_path: str, dataset_dir: Path
    ) -> Dict[str, int]:
        """Organize images into class directories based on annotations.

        Args:
            annotations: List of annotation objects from Label Studio
            storage_path: Path to storage containing original images
            dataset_dir: Directory to organize the dataset

        Returns:
            Dictionary with class names and image counts
        """
        class_counts = {}
        storage_path_obj = Path(storage_path)

        for annotation in annotations:
            try:
                # Extract image information
                image_filename = annotation.get("data", {}).get("filename")
                if not image_filename:
                    logger.warning(
                        f"No filename found in annotation {annotation.get('id')}"
                    )
                    continue

                # Extract class label from annotations
                class_label = self._extract_class_from_annotation(annotation)
                if not class_label:
                    logger.warning(f"No class label found for {image_filename}")
                    continue

                # Create class directory
                class_dir = dataset_dir / class_label
                class_dir.mkdir(exist_ok=True)

                # Copy image to class directory
                source_image_path = storage_path_obj / image_filename
                target_image_path = class_dir / image_filename

                if source_image_path.exists():
                    # Copy the image file
                    with (
                        open(source_image_path, "rb") as src,
                        open(target_image_path, "wb") as dst,
                    ):
                        dst.write(src.read())

                    class_counts[class_label] = class_counts.get(class_label, 0) + 1
                    logger.debug(f"Copied {image_filename} to class {class_label}")
                else:
                    # Try to extract image from base64 data if available
                    image_data = annotation.get("data", {}).get("image")
                    if image_data and image_data.startswith("data:"):
                        try:
                            self._save_base64_image(image_data, target_image_path)
                            class_counts[class_label] = (
                                class_counts.get(class_label, 0) + 1
                            )
                            logger.debug(
                                f"Saved base64 image {image_filename} to class {class_label}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to save base64 image {image_filename}: {e}"
                            )
                    else:
                        logger.warning(f"Source image not found: {source_image_path}")

            except Exception as e:
                logger.error(f"Failed to process annotation: {e}")
                continue

        return class_counts

    def _extract_class_from_annotation(
        self, annotation: Dict[str, Any]
    ) -> Optional[str]:
        """Extract class label from Label Studio annotation.

        Args:
            annotation: Single annotation object

        Returns:
            Class label string or None if not found
        """
        annotations_list = annotation.get("annotations", [])
        if not annotations_list:
            return None

        # Take the first annotation (assuming single label)
        first_annotation = annotations_list[0]
        result = first_annotation.get("result", [])

        if not result:
            return None

        # Look for choices result
        for item in result:
            if item.get("type") == "choices":
                choices = item.get("value", {}).get("choices", [])
                if choices:
                    return choices[0]  # Return first choice

        return None

    def _save_base64_image(self, image_data: str, target_path: Path) -> None:
        """Save base64 encoded image to file.

        Args:
            image_data: Base64 data URL string
            target_path: Path where to save the image
        """
        try:
            # Parse base64 data URL
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)

            # Save image
            with open(target_path, "wb") as f:
                f.write(image_bytes)

        except Exception as e:
            logger.error(f"Failed to save base64 image: {e}")
            raise

    def _validate_pytorch_imagefolder_format(self, zip_buffer: BytesIO) -> None:
        """Validate that the ZIP file contains proper PyTorch ImageFolder structure.

        Args:
            zip_buffer: ZIP file buffer to validate
        """
        zip_buffer.seek(0)

        try:
            with zipfile.ZipFile(zip_buffer, "r") as zip_file:
                file_list = zip_file.namelist()

                if not file_list:
                    raise Exception("ZIP file is empty")

                # Check that all files are in class subdirectories
                valid_structure = True
                class_dirs = set()

                for file_path in file_list:
                    path_parts = file_path.split("/")

                    # Should have exactly 2 parts: class_name/image_file
                    if len(path_parts) != 2:
                        valid_structure = False
                        logger.error(f"Invalid path structure: {file_path}")
                        break

                    class_name, filename = path_parts
                    class_dirs.add(class_name)

                    # Check if it's an image file
                    if not filename.lower().endswith(
                        (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
                    ):
                        logger.warning(f"Non-image file in dataset: {file_path}")

                if not valid_structure:
                    raise Exception(
                        "ZIP file does not follow PyTorch ImageFolder format"
                    )

                logger.info(
                    f"Validated PyTorch ImageFolder format: {len(class_dirs)} classes, {len(file_list)} images"
                )

        except zipfile.BadZipFile:
            raise Exception("Invalid ZIP file format")
        except Exception as e:
            raise Exception(f"ZIP validation failed: {e}")
