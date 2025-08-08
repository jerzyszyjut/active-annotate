from typing import Tuple, List, Optional
import os
import glob
import datetime
import torch
import torch.nn as nn
from torch import Tensor
from torch.optim import Optimizer
import pytorch_lightning as pl
import torchvision.models as models
import torchvision.transforms as transforms
import torchmetrics
from torchmetrics import Metric
from PIL import Image
from abc import ABC
import logging

logger = logging.getLogger(__name__)


class BaseImageClassificationModel(ABC):
    def predict(self, image: Image.Image) -> tuple[str, float]:
        raise NotImplementedError("Subclasses must implement predict method")

    def get_version(self) -> str:
        raise NotImplementedError("Subclasses must implement predict method")

    def get_name(self) -> str:
        raise NotImplementedError("Subclasses must implement predict method")


class ResNetImageClassificactionMLModel(
    pl.LightningModule, BaseImageClassificationModel
):
    def __init__(
        self,
        num_classes: int = 3,
        learning_rate: float = 1e-3,
        weights_dir: str = "model_weights",
        class_names: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.save_hyperparameters()
        self.num_classes: int = num_classes
        self.learning_rate: float = learning_rate
        self.weights_dir: str = weights_dir
        self.class_names: List[str] = class_names or [
            f"class_{i}" for i in range(num_classes)
        ]

        # Create weights directory if it doesn't exist
        os.makedirs(self.weights_dir, exist_ok=True)

        self.model: models.ResNet = models.resnet18(pretrained=True)

        # Initialize criterion and metrics
        self.criterion: nn.CrossEntropyLoss = nn.CrossEntropyLoss()
        self.train_acc: Metric = torchmetrics.Accuracy(
            task="multiclass", num_classes=num_classes
        )
        self.val_acc: Metric = torchmetrics.Accuracy(
            task="multiclass", num_classes=num_classes
        )
        self.test_acc: Metric = torchmetrics.Accuracy(
            task="multiclass", num_classes=num_classes
        )

        self.set_num_classes(num_classes)

        self._load_latest_weights()

    def _load_latest_weights(self) -> None:
        """Load the latest weights file from the weights directory"""
        try:
            weight_pattern = os.path.join(self.weights_dir, "*.pth")
            weight_files = glob.glob(weight_pattern)

            if weight_files:
                newest_file = max(weight_files, key=os.path.getmtime)
                print(f"Loading latest weights from {newest_file}")
                self.load_weights(newest_file)
                self._set_loaded_weights_path(newest_file)
                return

            print(
                f"No existing weights found in {self.weights_dir}, using pretrained ResNet weights"
            )
            self._set_loaded_weights_path("pretrained_resnet")

        except Exception as e:
            print(f"Warning: Failed to load weights: {e}")
            print("Continuing with pretrained ResNet weights")
            self._set_loaded_weights_path("pretrained_resnet")

    def forward(self, x: Tensor) -> Tensor:
        return self.model(x)

    def training_step(self, batch: Tuple[Tensor, Tensor], batch_idx: int) -> Tensor:
        x, y = batch
        logits = self(x)

        loss = self.criterion(logits, y)

        preds = torch.argmax(logits, dim=1)
        train_acc = self.train_acc(preds, y)

        self.log("train_loss", loss, prog_bar=True, on_epoch=True)
        self.log("train_acc", train_acc, prog_bar=True, on_epoch=True)
        return loss

    def validation_step(self, batch: Tuple[Tensor, Tensor], batch_idx: int) -> Tensor:
        x, y = batch
        logits = self(x)

        loss = self.criterion(logits, y)

        preds = torch.argmax(logits, dim=1)

        val_acc = self.val_acc(preds, y)

        self.log("val_loss", loss, prog_bar=True, on_epoch=True)
        self.log("val_acc", val_acc, prog_bar=True, on_epoch=True)
        return loss

    def test_step(self, batch: Tuple[Tensor, Tensor], batch_idx: int) -> Tensor:
        x, y = batch
        logits = self(x)

        loss = self.criterion(logits, y)

        preds = torch.argmax(logits, dim=1)
        test_acc = self.test_acc(preds, y)

        self.log("test_loss", loss, prog_bar=True, on_epoch=True)
        self.log("test_acc", test_acc, prog_bar=True, on_epoch=True)
        return loss

    def configure_optimizers(self) -> Optimizer:
        optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        return optimizer

    def predict(self, image: Image.Image) -> tuple[str, float]:
        """
        Predict class and confidence for an image.

        Returns:
            tuple: (predicted_class_name, confidence_score)
        """
        self.eval()

        transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        image_tensor: Tensor = transform(image)  # pyright: ignore[reportAssignmentType]

        image_tensor = image_tensor.unsqueeze(0)

        with torch.no_grad():
            output = self.forward(image_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted_class_idx = torch.max(probabilities, dim=1)

            predicted_class_idx = int(predicted_class_idx.item())
            confidence_score = float(confidence.item())

        # Return class name and confidence
        if predicted_class_idx < len(self.class_names):
            class_name = self.class_names[predicted_class_idx]
        else:
            class_name = f"class_{predicted_class_idx}"

        return class_name, confidence_score

    def get_version(self) -> str:
        return "1.0.0"

    def get_name(self) -> str:
        return "ResNetImageClassificactionMLModel"

    def set_num_classes(self, new_num_classes: int) -> None:
        if self.num_classes != new_num_classes:
            logger.info(
                f"Updating model from {self.num_classes} to {new_num_classes} classes"
            )
            in_features: int = self.model.fc.in_features
            self.model.fc = nn.Linear(in_features, new_num_classes)
            self.num_classes = new_num_classes

            # Update metrics for new number of classes
            self.train_acc = torchmetrics.Accuracy(
                task="multiclass", num_classes=new_num_classes
            )
            self.val_acc = torchmetrics.Accuracy(
                task="multiclass", num_classes=new_num_classes
            )
            self.test_acc = torchmetrics.Accuracy(
                task="multiclass", num_classes=new_num_classes
            )
        else:
            # Even if num_classes is the same, we still need to update the final layer
            in_features: int = self.model.fc.in_features
            self.model.fc = nn.Linear(in_features, new_num_classes)

    def save_weights(self, filename: str | None = None) -> str:
        """Save model weights and class names to the weights directory with timestamp"""
        if filename is None:
            # Generate timestamped filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"model_weights_{timestamp}.pth"

        filepath = os.path.join(self.weights_dir, filename)

        # Save both state dict and class names
        save_data = {
            "state_dict": self.state_dict(),
            "class_names": self.class_names,
            "num_classes": self.num_classes,
        }
        torch.save(save_data, filepath)
        print(f"Weights and class names saved to {filepath}")
        return filepath

    def load_weights(self, path: str) -> None:
        """Load model weights and class names from file"""
        checkpoint = torch.load(path, map_location="cpu")

        # Handle both old format (just state_dict) and new format (with class_names)
        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            self.load_state_dict(checkpoint["state_dict"])
            if "class_names" in checkpoint:
                self.class_names = checkpoint["class_names"]
                logger.info(f"Loaded class names: {self.class_names}")
            if "num_classes" in checkpoint:
                saved_num_classes = checkpoint["num_classes"]
                if saved_num_classes != self.num_classes:
                    logger.info(
                        f"Updating num_classes from {self.num_classes} to {saved_num_classes}"
                    )
                    self.set_num_classes(saved_num_classes)
        else:
            # Old format - just state dict
            self.load_state_dict(checkpoint)
            logger.warning("Loaded weights in old format - class names not available")

        self.eval()
        self._set_loaded_weights_path(path)

    def get_training_status(self) -> dict:
        return {
            "model_name": self.get_name(),
            "version": self.get_version(),
            "num_classes": self.num_classes,
            "learning_rate": self.learning_rate,
            "is_training": self.training,
            "weights_loaded_from": getattr(self, "_loaded_weights_path", "pretrained"),
        }

    def _set_loaded_weights_path(self, path: str) -> None:
        self._loaded_weights_path = path

    def reload_latest_weights(self) -> str:
        """Manually reload the latest weights and return the path that was loaded"""
        old_path = getattr(self, "_loaded_weights_path", "unknown")
        self._load_latest_weights()
        new_path = getattr(self, "_loaded_weights_path", "unknown")
        return f"Reloaded weights: {old_path} -> {new_path}"

    def list_available_weights(self) -> list[dict]:
        """List all available weight files with their metadata"""
        weight_pattern = os.path.join(self.weights_dir, "*.pth")
        weight_files = glob.glob(weight_pattern)

        weights_info = []
        for filepath in weight_files:
            filename = os.path.basename(filepath)
            stat = os.stat(filepath)
            weights_info.append(
                {
                    "filename": filename,
                    "filepath": filepath,
                    "size_bytes": stat.st_size,
                    "modified_time": datetime.datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat(),
                    "is_current": filepath == getattr(self, "_loaded_weights_path", ""),
                }
            )

        # Sort by modification time, newest first
        weights_info.sort(key=lambda x: x["modified_time"], reverse=True)
        return weights_info

    def get_weights_directory_info(self) -> dict:
        """Get information about the weights directory"""
        weights_list = self.list_available_weights()
        return {
            "weights_directory": self.weights_dir,
            "total_weight_files": len(weights_list),
            "current_loaded_weights": getattr(
                self, "_loaded_weights_path", "pretrained"
            ),
            "available_weights": weights_list,
        }

    def cleanup_old_weights(self, keep_count: int = 5) -> dict:
        """Keep only the newest N weight files, delete older ones"""
        weights_list = self.list_available_weights()

        if len(weights_list) <= keep_count:
            return {
                "message": f"No cleanup needed. Only {len(weights_list)} weights found (keeping {keep_count})",
                "deleted_files": [],
            }

        # Sort by modification time (newest first) and get files to delete
        weights_to_delete = weights_list[keep_count:]
        deleted_files = []

        for weight_info in weights_to_delete:
            try:
                os.remove(weight_info["filepath"])
                deleted_files.append(weight_info["filename"])
                print(f"Deleted old weights: {weight_info['filename']}")
            except Exception as e:
                print(f"Failed to delete {weight_info['filename']}: {e}")

        return {
            "message": f"Cleanup completed. Kept {keep_count} newest weights, deleted {len(deleted_files)} old weights",
            "deleted_files": deleted_files,
        }
