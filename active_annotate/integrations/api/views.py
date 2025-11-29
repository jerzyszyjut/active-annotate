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
from active_annotate.integrations.tasks import start_active_learning_loop
from active_annotate.integrations.tasks import step_in_active_learning_loop


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
    permission_classes = (AllowAny,)
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="start-active-learning",
    )
    def start_active_learning(self, request):
        serializer = StartActiveLearningLoopSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        dataset_id = data["dataset_id"]
        dataset = ClassificationDataset.objects.get(pk=dataset_id)
        
        if dataset.state == "in-progress":
            return Response({"status": "Active learning loop is in progress"})
        elif dataset.state == "finished":
            return Response(
                {"status": "Active learning loop is finished. Export annotations or create a new project."}
            )

        start_active_learning_loop.delay(dataset_id=dataset_id)

        return Response({"status": "Active learning started"})

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
            dataset=datapoint.dataset,
            class_label=data.annotation.result[-1].value.choices[0],
        )

        datapoint.label = label
        datapoint.save()

        if data.project.finished_task_number == datapoint.dataset.batch_size:
            step_in_active_learning_loop.delay(
                dataset_id=datapoint.dataset.id,
                project_id=data.project.id,
            )

        return Response({"status": "webhook received"})
