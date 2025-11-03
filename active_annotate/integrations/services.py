import base64

from django.db.models.enums import TextChoices
from django.urls import reverse
from label_studio_sdk import LabelStudio
from rest_framework.request import Request

from active_annotate.datasets.models import ClassificationDataset


class ActionTypes(TextChoices):
    ANNOTATION_CREATED = "ANNOTATION_CREATED"
    ANNOTATION_UPDATED = "ANNOTATION_UPDATED"


class LabelStudioService:
    def __init__(self, dataset: ClassificationDataset, request: Request):
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

    def create_project(self):
        project = None
        try:
            project = self.client.projects.create(
                label_config=self._get_image_classification_label_config(),
            )
            self.client.webhooks.create(
                url=self.request.build_absolute_uri(
                    reverse("integrations:label-studio-annotations-webhook"),
                ),
                project=project.id,
                actions=ActionTypes.values,
                send_payload=True,
                headers={"project_pk": str(self.dataset.pk)},
            )
            self.import_datapoints(project.id)
        except Exception:
            if project:
                self.client.projects.delete(project.id)
            raise
        return project

    def import_datapoints(self, project_id: int):
        for datapoint in self.dataset.datapoints.all():
            file_content = datapoint.file.read()
            base64_encoded = base64.b64encode(file_content).decode("utf-8")

            self.client.tasks.create(
                project=project_id,
                data={
                    "image": f"data:image/jpeg;base64,{base64_encoded}",
                },
                inner_id=datapoint.id,
            )
