from django.db import models
from django.db.models import FileField
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models.fields import CharField
from django.db.models.fields import PositiveIntegerField
from django.utils.translation import gettext_lazy as _


class Dataset(Model):
    name = CharField(_("Name"), max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Datapoint(Model):
    class Meta:
        abstract = True

    def __str__(self):
        return f"Datapoint {self.pk}"


class ClassificationDataset(Dataset):
    def __str__(self):
        return f"Classification Dataset: {self.name}"


class ClassificationLabel(Model):
    dataset = ForeignKey(
        ClassificationDataset,
        on_delete=models.CASCADE,
        related_name="labels",
    )
    class_index = PositiveIntegerField(_("Class ID"))
    class_label = CharField(_("Class Label"), max_length=255)

    class Meta:
        unique_together = (("dataset", "class_index"),)

    def __str__(self):
        return f"{self.dataset.name} - {self.class_label} (ID: {self.class_index})"


class ClassificationDatapoint(Datapoint):
    file = FileField(_("File"))
    label = ForeignKey(
        ClassificationLabel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datapoints",
    )
    dataset = ForeignKey(
        ClassificationDataset,
        on_delete=models.CASCADE,
        related_name="datapoints",
    )

    def __str__(self):
        return f"Datapoint {self.pk} in {self.dataset.name}"


class ClassificationPrediction(Datapoint):
    datapoint = ForeignKey(
        ClassificationDatapoint,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    predicted_label = ForeignKey(
        ClassificationLabel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="predictions",
    )
    confidence = models.FloatField(_("Confidence"), null=True, blank=True)

    def __str__(self):
        return (
            f"Prediction for Datapoint {self.datapoint.pk} - "
            f"Predicted: {self.predicted_label} (Confidence: {self.confidence})"
        )
