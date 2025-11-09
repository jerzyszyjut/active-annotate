import contextlib
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

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_transform_augmented():
    """Get image transforms with data augmentation for training."""
    return transforms.Compose(
        [
            transforms.Resize(256),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ],
    )


def get_transform():
    """Get image transforms for inference (no augmentation)."""
    return transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
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
        # Label smoothing reduces overconfidence and mode collapse
        self.criterion: nn.CrossEntropyLoss = nn.CrossEntropyLoss(
            label_smoothing=0.1,
        )
        self.train_acc: torchmetrics.Metric = torchmetrics.Accuracy(
            task="multiclass",
            num_classes=num_classes,
        )

        self.set_num_classes(num_classes)

    def set_num_classes(self, new_num_classes: int) -> None:
        # Determine in_features from current classifier. The fc attribute
        # may be either an nn.Linear or an nn.Sequential containing a
        # dropout and a linear layer. Search for the Linear module.
        in_features = None
        fc = self.model.fc
        if isinstance(fc, nn.Linear):
            in_features = fc.in_features
        elif isinstance(fc, nn.Sequential):
            for module in fc:
                if isinstance(module, nn.Linear):
                    in_features = module.in_features
                    break

        if in_features is None:
            # As a fallback, infer by forwarding a dummy tensor with the
            # conv backbone and measuring the feature size.
            with torch.no_grad():
                dummy = torch.zeros((1, 3, 224, 224))
                # Temporarily replace fc with Identity to get features
                orig_fc = self.model.fc
                try:
                    self.model.fc = nn.Identity()
                    out = self.model(dummy)
                    # out shape is (1, C)
                    in_features = out.shape[1]
                finally:
                    self.model.fc = orig_fc

        # Build a new classifier: dropout followed by linear
        linear = nn.Linear(in_features, new_num_classes)
        self.model.fc = nn.Sequential(nn.Dropout(p=0.5), linear)
        self.num_classes = new_num_classes
        # Recreate accuracy metric with the new number of classes
        self.train_acc = torchmetrics.Accuracy(
            task="multiclass",
            num_classes=new_num_classes,
        )

        # Ensure classifier is on the same device (device may not be set yet)
        with contextlib.suppress(Exception):
            self.model.fc.to(self.device)

    def reset_backbone_to_imagenet(
        self,
        weights: ResNet18_Weights | None = ResNet18_Weights.IMAGENET1K_V1,
    ) -> None:
        """Reload ResNet18 backbone weights (ImageNet) and reattach classifier.

        This replaces `self.model` with a fresh ResNet and reattaches a
        classifier for `self.num_classes`. Useful to start training from a
        consistent ImageNet-initialized backbone each training run.
        """
        # Create fresh resnet with requested weights
        self.model = models.resnet18(weights=weights)
        # Re-attach classifier for the current number of classes
        # set_num_classes will add dropout + linear
        self.set_num_classes(self.num_classes)

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
