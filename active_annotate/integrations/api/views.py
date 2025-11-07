from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.datasets.models import ClassificationLabel
from active_annotate.integrations.api.serializers import (
    StartActiveLearningLoopSerializer,
)
from active_annotate.integrations.label_studio_schemas import (
    LabelStudioAnnotationWebhookModel,
)


@extend_schema_view(
    start_active_learning=extend_schema(
        request=StartActiveLearningLoopSerializer,
        responses=OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Active learning started",
        ),
    ),
    webhook=extend_schema(
        request=None,
        responses=OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Webhook received",
        ),
    ),
)
class LabelStudioIntegrationViewSet(GenericViewSet):
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def start_active_learning(self, request):
        serializer = StartActiveLearningLoopSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        ClassificationDataset.objects.get(pk=data["dataset_id"])

        return Response({"status": "active learning started"})

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="annotations-webhook",
    )
    def annotations_webhook(self, request):
        data = LabelStudioAnnotationWebhookModel(**request.data)

        datapoint = ClassificationDatapoint.objects.get(pk=data.task.inner_id)
        label = ClassificationLabel.objects.get(
            class_label=data.annotation.result[-1].value.choices[0],
        )

        datapoint.label = label
        datapoint.save()

        return Response({"status": "webhook received"})
