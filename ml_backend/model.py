import logging
from pathlib import Path

import pytorch_lightning as pl
import torch
import torchmetrics
from PIL import Image
from torch import Tensor
from torch import nn
from torch.optim import Optimizer
from torchvision import models
from torchvision import transforms
from torchvision.models import ResNet18_Weights

logger = logging.getLogger(__name__)


def get_transform():
    return transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ],
    )


class ResNetImageClassificationMLModel(
    pl.LightningModule,
):
    def __init__(
        self,
        save_weights_dir: Path,
        num_classes: int = 1000,
        weights: str | None = None,
    ) -> None:
        super().__init__()
        self.num_classes: int = num_classes
        self.save_weights_dir: Path = save_weights_dir
        self.model: models.ResNet = models.resnet18(
            weights=ResNet18_Weights.IMAGENET1K_V1 if weights is None else weights,
        )
        self.criterion: nn.CrossEntropyLoss = nn.CrossEntropyLoss()
        self.train_acc: torchmetrics.Metric = torchmetrics.Accuracy(
            task="multiclass",
            num_classes=num_classes,
        )
        self.val_acc: torchmetrics.Metric = torchmetrics.Accuracy(
            task="multiclass",
            num_classes=num_classes,
        )
        self.test_acc: torchmetrics.Metric = torchmetrics.Accuracy(
            task="multiclass",
            num_classes=num_classes,
        )

        self.set_num_classes(num_classes)

    def set_num_classes(self, new_num_classes: int) -> None:
        in_features: int = self.model.fc.in_features
        self.model.fc = nn.Linear(in_features, new_num_classes)
        self.num_classes = new_num_classes

    def save_weights(self, version: int) -> None:
        filepath = self.save_weights_dir / f"model_weights_v{version}.pth"
        torch.save(self.state_dict(), filepath)

    def forward(self, x: Tensor) -> Tensor:
        return self.model(x)

    def training_step(self, batch: tuple[Tensor, Tensor]) -> Tensor:
        x, y = batch
        logits = self(x)

        loss = self.criterion(logits, y)

        preds = torch.argmax(logits, dim=1)
        train_acc = self.train_acc(preds, y)

        self.log("train_loss", loss, prog_bar=True, on_epoch=True)
        self.log("train_acc", train_acc, prog_bar=True, on_epoch=True)
        return loss

    def validation_step(self, batch: tuple[Tensor, Tensor]) -> Tensor:
        x, y = batch
        logits = self(x)

        loss = self.criterion(logits, y)

        preds = torch.argmax(logits, dim=1)

        val_acc = self.val_acc(preds, y)

        self.log("val_loss", loss, prog_bar=True, on_epoch=True)
        self.log("val_acc", val_acc, prog_bar=True, on_epoch=True)
        return loss

    def test_step(self, batch: tuple[Tensor, Tensor]) -> Tensor:
        x, y = batch
        logits = self(x)

        loss = self.criterion(logits, y)

        preds = torch.argmax(logits, dim=1)
        test_acc = self.test_acc(preds, y)

        self.log("test_loss", loss, prog_bar=True, on_epoch=True)
        self.log("test_acc", test_acc, prog_bar=True, on_epoch=True)
        return loss

    def configure_optimizers(self) -> Optimizer:
        return torch.optim.Adam(self.parameters(), lr=1e-3)

    def predict(self, image: Image.Image) -> Tensor:
        self.eval()

        if image.mode != "RGB":
            image = image.convert("RGB")

        transform = get_transform()

        image_tensor = transform(image)
        image_tensor = image_tensor.unsqueeze(0)

        with torch.no_grad():
            output = self.forward(image_tensor)
            return torch.softmax(output, dim=1)
