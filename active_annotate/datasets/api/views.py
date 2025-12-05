from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from active_annotate.datasets.api.serializers import ClassificationDatapointSerializer
from active_annotate.datasets.api.serializers import ClassificationDatasetSerializer
from active_annotate.datasets.api.serializers import ClassificationLabelSerializer
from active_annotate.datasets.api.serializers import ClassificationPredictionSerializer
from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.datasets.models import ClassificationLabel
from active_annotate.datasets.models import ClassificationPrediction


class ClassificationDatasetViewSet(ModelViewSet):
    queryset = ClassificationDataset.objects.all()
    serializer_class = ClassificationDatasetSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=["get"], url_path="export")
    def export_dataset(self, request, pk=None):
        dataset = self.get_object()
        datapoints = (
            dataset.datapoints.all()
            .select_related("label")
            .prefetch_related(
                "predictions__predicted_label",
            )
        )

        export_data = {
            "dataset": {
                "id": dataset.id,
                "name": dataset.name,
                "batch_size": dataset.batch_size,
                "uncertainty_strategy": dataset.uncertainty_strategy,
                "epoch": dataset.epoch,
                "max_epochs": dataset.max_epochs,
                "state": dataset.state,
            },
            "labels": [
                {
                    "id": label.id,
                    "class_index": label.class_index,
                    "class_label": label.class_label,
                }
                for label in dataset.labels.all()
            ],
            "datapoints": [
                {
                    "id": datapoint.id,
                    "file_url": request.build_absolute_uri(datapoint.file.url)
                    if datapoint.file
                    else None,
                    "label": {
                        "id": datapoint.label.id,
                        "class_index": datapoint.label.class_index,
                        "class_label": datapoint.label.class_label,
                    }
                    if datapoint.label
                    else None,
                    "predictions": [
                        {
                            "id": pred.id,
                            "model_version": pred.model_version,
                            "confidence": pred.confidence,
                            "predicted_label": {
                                "id": pred.predicted_label.id,
                                "class_index": pred.predicted_label.class_index,
                                "class_label": pred.predicted_label.class_label,
                            }
                            if pred.predicted_label
                            else None,
                        }
                        for pred in datapoint.predictions.all()
                    ],
                }
                for datapoint in datapoints
            ],
        }

        return JsonResponse(export_data, safe=False)


class ClassificationLabelViewSet(ModelViewSet):
    queryset = ClassificationLabel.objects.all()
    serializer_class = ClassificationLabelSerializer
    permission_classes = (IsAuthenticated,)


class ClassificationDatapointViewSet(ModelViewSet):
    queryset = ClassificationDatapoint.objects.all()
    serializer_class = ClassificationDatapointSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)


class ClassificationPredictionViewSet(ModelViewSet):
    queryset = ClassificationPrediction.objects.all()
    serializer_class = ClassificationPredictionSerializer
    permission_classes = (IsAuthenticated,)
