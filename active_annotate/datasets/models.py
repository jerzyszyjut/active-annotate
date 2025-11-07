from django.db import models
from django.db.models import Exists
from django.db.models import FileField
from django.db.models import ForeignKey
from django.db.models import Max
from django.db.models import Model
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models.fields import CharField
from django.db.models.fields import PositiveIntegerField
from django.utils.translation import gettext_lazy as _


class Dataset(Model):
    name = CharField(_("Name"), max_length=255)
    label_studio_url = CharField(_("Label Studio URL"), max_length=255)
    label_studio_api_key = CharField(_("Label Studio API Key"), max_length=255)
    ml_backend_url = CharField(_("ML Backend URL"), max_length=255)
    batch_size = PositiveIntegerField(
        _("Batch Size"),
        default=16,
        help_text=_("Number of datapoints to process in each batch."),
    )

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


class ClassificationDatapointQuerySet(models.QuerySet):
    def without_predictions_for_version(self, version):
        predictions_for_dp = ClassificationPrediction.objects.filter(
            datapoint=OuterRef("pk"),
            model_version=version,
        ).values("pk")[:1]

        return self.annotate(has_prediction=Exists(predictions_for_dp)).filter(
            has_prediction=False,
        )


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

    objects = ClassificationDatapointQuerySet.as_manager()

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
    model_version = PositiveIntegerField(_("Model Version"))

    def __str__(self):
        return (
            f"Prediction for Datapoint {self.datapoint.pk} - "
            f"Predicted: {self.predicted_label} (Confidence: {self.confidence})"
        )

    @staticmethod
    def latest_confidence_subquery(version):
        return Subquery(
            ClassificationPrediction.objects.filter(
                datapoint=OuterRef("pk"),
                model_version=version,
            )
            .values("datapoint")
            .annotate(latest_conf=Max("confidence"))
            .values("latest_conf"),
        )
