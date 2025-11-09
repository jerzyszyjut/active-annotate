import json
import logging
import os
from enum import Enum
from pathlib import Path

import pytorch_lightning as pl
import torch
from filelock import FileLock
from model import ResNetImageClassificationMLModel
from model import get_transform_augmented
from pytorch_lightning.callbacks import Callback
from torch.utils.data import DataLoader
from torchvision import datasets

logger = logging.getLogger("uvicorn.error")
if not logger.handlers:
    logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TrainingLoggingCallback(Callback):
    """Streams key Lightning metrics to the FastAPI logs."""

    def on_train_epoch_start(self, trainer, pl_module) -> None:  # type: ignore[override]
        logger.info(
            "Epoch %s starting (%s total epochs)",
            trainer.current_epoch,
            trainer.max_epochs,
        )

    def on_train_epoch_end(self, trainer, pl_module) -> None:  # type: ignore[override]
        metrics = trainer.callback_metrics
        train_loss = metrics.get("train_loss")
        train_acc = metrics.get("train_acc")
        logger.info(
            "Epoch %s training complete | loss=%s acc=%s",
            trainer.current_epoch,
            _format_metric(train_loss),
            _format_metric(train_acc),
        )

    def on_validation_epoch_end(self, trainer, pl_module) -> None:  # type: ignore[override]
        metrics = trainer.callback_metrics
        val_loss = metrics.get("val_loss")
        val_acc = metrics.get("val_acc")
        logger.info(
            "Epoch %s validation complete | val_loss=%s val_acc=%s",
            trainer.current_epoch,
            _format_metric(val_loss),
            _format_metric(val_acc),
        )


def _format_metric(value) -> str:
    if value is None:
        return "-"
    if hasattr(value, "item"):
        return f"{value.item():.4f}"
    return f"{value:.4f}"


def _resolve_dataset_root(base_path: Path) -> Path:
    train_dir = base_path / "train"
    if train_dir.is_dir():
        return base_path

    for candidate_train in base_path.glob("**/train"):
        return candidate_train.parent

    msg = f"Expected to find 'train' directory under {base_path.resolve()}"
    raise FileNotFoundError(msg)


class ModelStatus(str, Enum):
    IDLE = "idle"
    TRAINING = "training"


class ModelManager:
    def __init__(self, save_weights_dir: Path, num_classes: int = 1000):
        self.save_weights_dir = save_weights_dir
        self.status_file = save_weights_dir / "model_status.json"
        self._lock = FileLock(str(save_weights_dir / "model.lock"), timeout=3)

        self.model = ResNetImageClassificationMLModel(save_weights_dir, num_classes)
        self.class_names: list[str] = []

        cpu_count = os.cpu_count() or 1
        env_workers = os.getenv("DATA_LOADER_WORKERS")
        if env_workers is not None:
            try:
                self.dataloader_workers = max(int(env_workers), 0)
            except ValueError:
                logger.warning(
                    "[training] invalid DATA_LOADER_WORKERS=%s; falling back to 0",
                    env_workers,
                )
                self.dataloader_workers = 0
        else:
            self.dataloader_workers = 0

        if self.dataloader_workers == 0 and cpu_count > 1:
            logger.info(
                "[training] using single-process data loading; "
                "set DATA_LOADER_WORKERS>0 to enable multiprocessing",
            )

        self._load_status()
        self._load_latest_weights()

    def _load_status(self) -> None:
        with self._lock:
            if self.status_file.exists():
                data = json.loads(self.status_file.read_text())
                self.status = ModelStatus(data.get("status", "idle"))
                self.version = data.get("version", 0)
            else:
                self.status = ModelStatus.IDLE
                self.version = 0
                self._save_status()

    def _save_status(self) -> None:
        data = {
            "status": self.status.value,
            "version": self.version,
        }
        self.status_file.write_text(json.dumps(data))

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

    def start_training(self) -> None:
        with self._lock:
            if self.status == ModelStatus.TRAINING:
                msg = "Training already in progress"
                raise RuntimeError(msg)
            self.status = ModelStatus.TRAINING
            self._save_status()

    def finish_training(self, *, succeeded: bool) -> None:
        with self._lock:
            self.status = ModelStatus.IDLE
            if succeeded:
                self.version += 1
            self._save_status()

    def train(
        self,
        data_path: Path,
        epochs: int = 10,
        batch_size: int = 32,
    ):
        self.start_training()

        succeeded = False
        try:
            dataset_root = _resolve_dataset_root(data_path)

            train_transform = get_transform_augmented()

            logger.info("[training] dataset_root=%s", dataset_root)

            train_dataset = datasets.ImageFolder(
                dataset_root / "train",
                transform=train_transform,
            )

            train_len = len(train_dataset)
            logger.info(
                "[training] train_samples=%s workers=%s",
                train_len,
                self.dataloader_workers,
            )

            num_classes = len(train_dataset.classes)

            # Always reset backbone to ImageNet weights before training so
            # each active-learning retrain starts from the same pretrained
            # initialization rather than from previous fine-tuned weights.
            try:
                self.model.reset_backbone_to_imagenet()
            except Exception:
                # If resetting fails for any reason, log and continue; subsequent
                # set_num_classes will still ensure the classifier is correct.
                logger.exception(
                    "[training] failed to reset backbone to ImageNet weights",
                )

            # Ensure classifier matches the current dataset's number of classes
            self.model.set_num_classes(num_classes)

            self.class_names = train_dataset.classes
            logger.info(
                "[training] num_classes=%s classes=%s",
                num_classes,
                self.class_names,
            )

            train_loader = DataLoader(
                train_dataset,
                batch_size=batch_size,
                shuffle=True,
                num_workers=self.dataloader_workers,
                persistent_workers=self.dataloader_workers > 0,
            )

            logger.info(
                "[training] starting trainer epochs=%s batch_size=%s",
                epochs,
                batch_size,
            )

            trainer = pl.Trainer(
                max_epochs=epochs,
                accelerator="auto",
                enable_progress_bar=False,
                log_every_n_steps=1,
                callbacks=[TrainingLoggingCallback()],
            )
            trainer.fit(self.model, train_loader)
            logger.info("[training] trainer finished successfully")
            self.model.save_weights(self.version + 1)
            logger.info("[training] weights saved version=%s", self.version + 1)
            succeeded = True
        finally:
            self.finish_training(succeeded=succeeded)
            logger.info(
                "[training] status=%s",
                "succeeded" if succeeded else "failed",
            )

    def can_predict(self) -> bool:
        with self._lock:
            return self.status == ModelStatus.IDLE

    def get_status(self) -> dict:
        with self._lock:
            return {
                "status": self.status.value,
                "version": self.version,
            }
