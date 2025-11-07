import base64

import httpx
from django.db.models.enums import TextChoices
from django.db.models.functions import Coalesce
from label_studio_sdk import LabelStudio
from rest_framework.request import Request

from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.datasets.models import ClassificationLabel
from active_annotate.datasets.models import ClassificationPrediction


class WebhookAnnotationActionTypes(TextChoices):
    ANNOTATION_CREATED = "ANNOTATION_CREATED"
    ANNOTATION_UPDATED = "ANNOTATION_UPDATED"


class MLBackendService:
    def __init__(self, dataset: ClassificationDataset):
        self.client = httpx.Client(base_url=dataset.ml_backend_url)
        self.dataset = dataset

    def get_model_version(self):
        response = self.client.get("/status").json()
        return response["version"]

    def infer_predictions(self):
        current_version = self.get_model_version()

        queryset = ClassificationDatapoint.objects.filter(
            dataset=self.dataset,
            label__isnull=True,
        ).without_predictions_for_version(current_version)

        predictions_to_create = []
        for datapoint in queryset:
            response = self.client.post(
                "/predict",
                files={
                    "file": datapoint.file.read(),
                },
            ).json()

            predictions_list = response.get("predictions", [])
            if predictions_list:
                for prediction in predictions_list[0]:
                    predicted_label = ClassificationLabel.objects.filter(
                        dataset=self.dataset,
                        class_index=prediction["idx"],
                    ).first()
                    predictions_to_create.append(
                        ClassificationPrediction(
                            datapoint=datapoint,
                            predicted_label=predicted_label,
                            confidence=prediction.get("confidence"),
                            model_version=response.get("version"),
                        ),
                    )

        if predictions_to_create:
            ClassificationPrediction.objects.bulk_create(predictions_to_create)


class ActiveLearningService:
    def __init__(self, dataset: ClassificationDataset):
        self.dataset = dataset

    def choose_points(self, version: int):
        queryset = ClassificationDatapoint.objects.filter(
            dataset=self.dataset,
            label__isnull=True,
        ).annotate(
            latest_prediction_confidence=ClassificationPrediction.latest_confidence_subquery(
                version,
            ),
        )

        points_ranked_by_uncertainty = queryset.order_by(
            Coalesce("latest_prediction_confidence", 0.0),
        )

        return points_ranked_by_uncertainty[: self.dataset.batch_size]


class LabelStudioService:
    def __init__(self, dataset: ClassificationDataset, request: Request = None):
        self.client = LabelStudio(
            base_url=dataset.label_studio_url,
            api_key=dataset.label_studio_api_key,
        )
        self.dataset = dataset
        self.request = request

    def _get_image_classification_label_config(self):
        return """
        <View>
          <Image name="image" value="$image"/>
          <Choices name="label" toName="image">
            {}
          </Choices>
        </View>
        """.format(
            "\n".join(
                [
                    f'<Choice value="{label.class_label}"/>'
                    for label in self.dataset.labels.order_by("class_index")
                ],
            ),
        )

    def create_active_learning_project(
        self,
        webhook_url: str | None = None,
        dataset_pk: int | None = None,
    ):
        project = self.client.projects.create(
            label_config=self._get_image_classification_label_config(),
        )

        if webhook_url and dataset_pk:
            self.client.webhooks.create(
                url=webhook_url,
                project=project.id,
                actions=WebhookAnnotationActionTypes.values,
                send_payload=True,
                send_for_all_actions=False,
                headers={"project_pk": str(dataset_pk)},
            )

        self.import_datapoints(project.id)
        return project

    def import_datapoints(self, project_id: int):
        ml_backend_service = MLBackendService(self.dataset)
        current_version = ml_backend_service.get_model_version()
        active_learning_service = ActiveLearningService(self.dataset)

        datapoints_to_import = active_learning_service.choose_points(current_version)

        for datapoint in datapoints_to_import:
            file_content = datapoint.file.read()
            base64_encoded = base64.b64encode(file_content).decode("utf-8")

            task = self.client.tasks.create(
                project=project_id,
                data={
                    "image": f"data:image/jpeg;base64,{base64_encoded}",
                },
                inner_id=datapoint.id,
            )

            latest_prediction = (
                datapoint.predictions.filter(
                    model_version=current_version,
                    predicted_label__isnull=False,
                )
                .order_by("-id")
                .first()
            )

            if (
                latest_prediction
                and latest_prediction.predicted_label
                and latest_prediction.confidence
            ):
                self.client.predictions.create(
                    task=task.id,
                    result=[
                        {
                            "value": {
                                "choices": [
                                    latest_prediction.predicted_label.class_label,
                                ],
                            },
                            "from_name": "label",
                            "to_name": "image",
                            "type": "choices",
                        },
                    ],
                    model_version=str(current_version),
                    score=float(latest_prediction.confidence),
                )
