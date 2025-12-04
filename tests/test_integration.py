import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.datasets.models import ClassificationLabel
from active_annotate.datasets.models import ClassificationPrediction

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",  # noqa: S106
    )


@pytest.mark.django_db
class TestDatasetWorkflow:
    def test_complete_dataset_workflow(self, api_client, user):
        dataset_data = {
            "name": "Integration Test Dataset",
            "label_studio_url": "http://localhost:8080",
            "label_studio_api_key": "integration-key",
            "ml_backend_url": "http://localhost:9090",
            "max_epochs": 3,
            "owner": user.id,
        }
        dataset_response = api_client.post(
            "/api/data/datasets/classification/",
            dataset_data,
        )
        assert dataset_response.status_code == 201  # noqa: PLR2004
        dataset_id = dataset_response.data["id"]

        label1_data = {
            "dataset": dataset_id,
            "class_index": 0,
            "class_label": "Cat",
        }
        label1_response = api_client.post(
            "/api/data/labels/classification/",
            label1_data,
        )
        assert label1_response.status_code == 201  # noqa: PLR2004

        label2_data = {
            "dataset": dataset_id,
            "class_index": 1,
            "class_label": "Dog",
        }
        label2_response = api_client.post(
            "/api/data/labels/classification/",
            label2_data,
        )
        assert label2_response.status_code == 201  # noqa: PLR2004

        test_file = SimpleUploadedFile(
            "cat.jpg",
            b"image_content",
            content_type="image/jpeg",
        )
        datapoint_data = {
            "file": test_file,
            "dataset": dataset_id,
            "class_index": 0,
        }
        datapoint_response = api_client.post(
            "/api/data/datapoints/classification/",
            datapoint_data,
            format="multipart",
        )
        assert datapoint_response.status_code == 201  # noqa: PLR2004
        datapoint_id = datapoint_response.data["id"]

        prediction_data = {
            "datapoint": datapoint_id,
            "predicted_class_index": 0,
            "confidence": 0.92,
            "model_version": 1,
        }
        prediction_response = api_client.post(
            "/api/data/predictions/classification/",
            prediction_data,
        )
        assert prediction_response.status_code == 201  # noqa: PLR2004

        dataset = ClassificationDataset.objects.get(id=dataset_id)
        assert dataset.labels.count() == 2  # noqa: PLR2004
        assert dataset.datapoints.count() == 1

        datapoint = ClassificationDatapoint.objects.get(id=datapoint_id)
        assert datapoint.label.class_label == "Cat"
        assert datapoint.predictions.count() == 1
        assert datapoint.predictions.first().confidence == 0.92  # noqa: PLR2004


@pytest.mark.django_db
class TestPredictionWorkflow:
    def test_multiple_predictions_per_datapoint(self, api_client, user):
        dataset = ClassificationDataset.objects.create(
            name="Prediction Test Dataset",
            label_studio_url="http://localhost:8080",
            label_studio_api_key="key",
            ml_backend_url="http://localhost:9090",
            max_epochs=5,
            owner=user,
        )

        label1 = ClassificationLabel.objects.create(
            dataset=dataset,
            class_index=0,
            class_label="Cat",
        )

        label2 = ClassificationLabel.objects.create(
            dataset=dataset,
            class_index=1,
            class_label="Dog",
        )

        test_file = SimpleUploadedFile(
            "image.jpg",
            b"content",
            content_type="image/jpeg",
        )
        datapoint = ClassificationDatapoint.objects.create(
            file=test_file,
            dataset=dataset,
            label=label1,
        )

        pred1_data = {
            "datapoint": datapoint.id,
            "predicted_class_index": 0,
            "confidence": 0.85,
            "model_version": 1,
        }
        pred1_response = api_client.post(
            "/api/data/predictions/classification/",
            pred1_data,
        )
        assert pred1_response.status_code == 201  # noqa: PLR2004

        pred2_data = {
            "datapoint": datapoint.id,
            "predicted_class_index": 1,
            "confidence": 0.92,
            "model_version": 2,
        }
        pred2_response = api_client.post(
            "/api/data/predictions/classification/",
            pred2_data,
        )
        assert pred2_response.status_code == 201  # noqa: PLR2004

        datapoint.refresh_from_db()
        assert datapoint.predictions.count() == 2  # noqa: PLR2004

        version1_predictions = ClassificationPrediction.objects.filter(
            datapoint=datapoint,
            model_version=1,
        )
        assert version1_predictions.count() == 1
        assert version1_predictions.first().predicted_label == label1

        version2_predictions = ClassificationPrediction.objects.filter(
            datapoint=datapoint,
            model_version=2,
        )
        assert version2_predictions.count() == 1
        assert version2_predictions.first().predicted_label == label2


@pytest.mark.django_db
class TestDatapointQueryset:
    def test_without_predictions_filter(self, user):
        dataset = ClassificationDataset.objects.create(
            name="Queryset Test Dataset",
            label_studio_url="http://localhost:8080",
            label_studio_api_key="key",
            ml_backend_url="http://localhost:9090",
            max_epochs=5,
            owner=user,
        )

        label = ClassificationLabel.objects.create(
            dataset=dataset,
            class_index=0,
            class_label="Cat",
        )

        file1 = SimpleUploadedFile("img1.jpg", b"content1", content_type="image/jpeg")
        datapoint1 = ClassificationDatapoint.objects.create(
            file=file1,
            dataset=dataset,
            label=label,
        )

        file2 = SimpleUploadedFile("img2.jpg", b"content2", content_type="image/jpeg")
        datapoint2 = ClassificationDatapoint.objects.create(
            file=file2,
            dataset=dataset,
            label=label,
        )

        version = 1
        without_predictions = (
            ClassificationDatapoint.objects.without_predictions_for_version(version)
        )
        assert datapoint1 in without_predictions
        assert datapoint2 in without_predictions

        ClassificationPrediction.objects.create(
            datapoint=datapoint1,
            predicted_label=label,
            confidence=0.9,
            model_version=version,
        )

        without_predictions = (
            ClassificationDatapoint.objects.without_predictions_for_version(version)
        )
        assert datapoint1 not in without_predictions
        assert datapoint2 in without_predictions


@pytest.mark.django_db
class TestCascadeDelete:
    def test_dataset_cascade_delete(self, user):
        dataset = ClassificationDataset.objects.create(
            name="Delete Test Dataset",
            label_studio_url="http://localhost:8080",
            label_studio_api_key="key",
            ml_backend_url="http://localhost:9090",
            max_epochs=5,
            owner=user,
        )

        label = ClassificationLabel.objects.create(
            dataset=dataset,
            class_index=0,
            class_label="Cat",
        )

        test_file = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        datapoint = ClassificationDatapoint.objects.create(
            file=test_file,
            dataset=dataset,
            label=label,
        )

        prediction = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.9,
            model_version=1,
        )

        dataset_id = dataset.id
        label_id = label.id
        datapoint_id = datapoint.id
        prediction_id = prediction.id

        dataset.delete()

        assert not ClassificationDataset.objects.filter(id=dataset_id).exists()
        assert not ClassificationLabel.objects.filter(id=label_id).exists()
        assert not ClassificationDatapoint.objects.filter(id=datapoint_id).exists()
        assert not ClassificationPrediction.objects.filter(id=prediction_id).exists()

    def test_label_set_null_on_delete(self, user):
        dataset = ClassificationDataset.objects.create(
            name="Label Delete Test",
            label_studio_url="http://localhost:8080",
            label_studio_api_key="key",
            ml_backend_url="http://localhost:9090",
            max_epochs=5,
            owner=user,
        )

        label = ClassificationLabel.objects.create(
            dataset=dataset,
            class_index=0,
            class_label="Cat",
        )

        test_file = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        datapoint = ClassificationDatapoint.objects.create(
            file=test_file,
            dataset=dataset,
            label=label,
        )

        label.delete()

        datapoint.refresh_from_db()
        assert datapoint.label is None
        assert ClassificationDatapoint.objects.filter(id=datapoint.id).exists()


@pytest.mark.django_db
class TestDatasetStateTransitions:
    def test_dataset_state_progression(self, user):
        dataset = ClassificationDataset.objects.create(
            name="State Test Dataset",
            label_studio_url="http://localhost:8080",
            label_studio_api_key="key",
            ml_backend_url="http://localhost:9090",
            max_epochs=3,
            owner=user,
        )

        assert dataset.state == "not-started"
        assert dataset.epoch == 0

        dataset.state = "in-progress"
        dataset.epoch = 1
        dataset.save()
        dataset.refresh_from_db()
        assert dataset.state == "in-progress"
        assert dataset.epoch == 1

        dataset.epoch = 2
        dataset.save()
        dataset.refresh_from_db()
        assert dataset.epoch == 2  # noqa: PLR2004

        dataset.epoch = 3
        dataset.state = "finished"
        dataset.save()
        dataset.refresh_from_db()
        assert dataset.state == "finished"
        assert dataset.epoch == 3  # noqa: PLR2004
