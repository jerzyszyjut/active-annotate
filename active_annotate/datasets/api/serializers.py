from rest_framework.serializers import ModelSerializer

from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.datasets.models import ClassificationLabel
from active_annotate.datasets.models import ClassificationPrediction


class ClassificationDatasetSerializer(ModelSerializer):
    class Meta:
        model = ClassificationDataset
        fields = "__all__"


class ClassificationLabelSerializer(ModelSerializer):
    class Meta:
        model = ClassificationLabel
        fields = "__all__"


class ClassificationDatapointSerializer(ModelSerializer):
    class Meta:
        model = ClassificationDatapoint
        fields = "__all__"


class ClassificationPredictionSerializer(ModelSerializer):
    class Meta:
        model = ClassificationPrediction
        fields = "__all__"
