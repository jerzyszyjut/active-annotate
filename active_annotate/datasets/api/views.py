from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
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
    permission_classes = (AllowAny,)


class ClassificationLabelViewSet(ModelViewSet):
    queryset = ClassificationLabel.objects.all()
    serializer_class = ClassificationLabelSerializer
    permission_classes = (AllowAny,)


class ClassificationDatapointViewSet(ModelViewSet):
    queryset = ClassificationDatapoint.objects.all()
    serializer_class = ClassificationDatapointSerializer
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser, FormParser)


class ClassificationPredictionViewSet(ModelViewSet):
    queryset = ClassificationPrediction.objects.all()
    serializer_class = ClassificationPredictionSerializer
    permission_classes = (AllowAny,)
