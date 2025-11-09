import base64
import math
import random
import shutil
import tempfile
from pathlib import Path

import httpx
from django.db.models.enums import TextChoices
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
                    if predicted_label is not None:
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

    def train_model(self):
        labeled_datapoints = ClassificationDatapoint.objects.filter(
            dataset=self.dataset,
            label__isnull=False,
        )

        temp_dir = Path(tempfile.mkdtemp())

        for split_name, split in [("train", labeled_datapoints)]:
            for datapoint in split:
                class_label_dir = (
                    temp_dir / "dataset" / split_name / datapoint.label.class_label
                )
                class_label_dir.mkdir(parents=True, exist_ok=True)
                with Path.open(
                    class_label_dir / Path(datapoint.file.name).name,
                    "wb",
                ) as f:
                    f.write(datapoint.file.read())

        zip_path = temp_dir / "dataset.zip"

        shutil.make_archive(str(zip_path.with_suffix("")), "zip", temp_dir / "dataset")

        with Path.open(zip_path, "rb") as f:
            self.client.post(
                "/train",
                files={
                    "file": f,
                },
            )

    def check_model_status(self):
        response = self.client.get("/status").json()
        return response["status"]


class ActiveLearningService:
    def __init__(self, dataset: ClassificationDataset):
        self.dataset = dataset
        self.uncertainty_strategy = self._entropy_uncertainty

    @staticmethod
    def _entropy_uncertainty(predictions: list[ClassificationPrediction]) -> float:
        if not predictions:
            return 1.0

        confidences = [p.confidence for p in predictions if p.confidence is not None]

        if not confidences:
            return 1.0

        total_confidence = sum(confidences)
        if total_confidence == 0:
            return 1.0

        probabilities = [conf / total_confidence for conf in confidences]
        entropy = -sum(p * math.log(p) for p in probabilities if p > 0)

        max_entropy = math.log(len(probabilities))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def set_uncertainty_strategy(self, strategy_func):
        self.uncertainty_strategy = strategy_func

    def _calculate_uncertainty(
        self,
        predictions: list[ClassificationPrediction],
    ) -> float:
        return self.uncertainty_strategy(predictions)

    def choose_points(self, version: int):
        datapoint_queryset = ClassificationDatapoint.objects.filter(
            dataset=self.dataset,
            label__isnull=True,
        )

        predictions_by_datapoint = {}
        for datapoint in datapoint_queryset:
            predictions = list(
                datapoint.predictions.filter(model_version=version),
            )
            if predictions:
                predictions_by_datapoint[datapoint] = predictions

        if not predictions_by_datapoint:
            all_datapoints = list(datapoint_queryset)
            return random.sample(
                all_datapoints,
                min(self.dataset.batch_size, len(all_datapoints)),
            )

        datapoints_with_uncertainty = [
            (datapoint, self._calculate_uncertainty(preds))
            for datapoint, preds in predictions_by_datapoint.items()
        ]

        points_ranked_by_uncertainty = sorted(
            datapoints_with_uncertainty,
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            datapoint
            for datapoint, _ in points_ranked_by_uncertainty[: self.dataset.batch_size]
        ]


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
                    for label in ClassificationLabel.objects.filter(
                        dataset=self.dataset,
                    ).order_by("class_index")
                ],
            ),
        )

    def create_active_learning_project(
        self,
    ):
        project = self.client.projects.create(
            title=f"Active Learning - {self.dataset.name}",
            label_config=self._get_image_classification_label_config(),
        )

        self.client.webhooks.create(
            url="http://django.django:8000/api/integrations/label-studio/annotations-webhook/",
            project=project.id,
            actions=WebhookAnnotationActionTypes.values,
            send_payload=True,
            send_for_all_actions=False,
            headers={"project_pk": str(self.dataset.pk)},
        )

        self.import_datapoints(project.id)

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
                .order_by("-confidence")
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

    def delete_project(self, project_id: int):
        self.client.projects.delete(project_id)
