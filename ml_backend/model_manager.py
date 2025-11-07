from enum import Enum
from pathlib import Path

import pytorch_lightning as pl
import torch
from filelock import FileLock
from model import ResNetImageClassificationMLModel
from torch.utils.data import DataLoader
from torchvision import datasets


class ModelStatus(str, Enum):
    IDLE = "idle"
    TRAINING = "training"


class ModelManager:
    def __init__(self, save_weights_dir: Path, num_classes: int = 1000):
        self.save_weights_dir = save_weights_dir
        self.model = ResNetImageClassificationMLModel(save_weights_dir, num_classes)
        self.status = ModelStatus.IDLE
        self.version = 0
        self._lock = FileLock("concurrent_gunicorn.lock", timeout=3)
        self.class_names: list[str] = []
        self._load_latest_weights()

    def _load_latest_weights(self):
        weight_files = sorted(self.save_weights_dir.glob("model_weights_v*.pth"))
        if weight_files:
            latest_weight = weight_files[-1]
            state_dict = torch.load(
                latest_weight,
                weights_only=True,
                map_location="cpu",
            )
            self.model.load_state_dict(state_dict)
            version_str = latest_weight.stem.replace("model_weights_v", "")
            self.version = int(version_str)

    def start_training(self):
        with self._lock:
            if self.status == ModelStatus.TRAINING:
                msg = "Training already in progress"
                raise RuntimeError(msg)
            self.status = ModelStatus.TRAINING

    def finish_training(self):
        with self._lock:
            self.status = ModelStatus.IDLE
            self.version += 1

    def train(
        self,
        data_path: Path,
        epochs: int = 10,
        batch_size: int = 32,
    ):
        try:
            self.start_training()

            train_dataset = datasets.ImageFolder(data_path / "train")
            val_dataset = datasets.ImageFolder(data_path / "val")

            num_classes = len(train_dataset.classes)
            if num_classes != self.model.num_classes:
                self.model.set_num_classes(num_classes)

            self.class_names = train_dataset.classes

            train_loader = DataLoader(
                train_dataset,
                batch_size=batch_size,
                shuffle=True,
            )
            val_loader = DataLoader(val_dataset, batch_size=batch_size)

            trainer = pl.Trainer(
                max_epochs=epochs,
                accelerator="auto",
                enable_progress_bar=False,
            )
            trainer.fit(self.model, train_loader, val_loader)
            self.model.save_weights(self.version + 1)
        finally:
            self.finish_training()

    def can_predict(self) -> bool:
        with self._lock:
            return self.status == ModelStatus.IDLE

    def get_status(self) -> dict:
        with self._lock:
            return {
                "status": self.status.value,
                "version": self.version,
            }
