import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
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


@pytest.fixture
def dataset(user):
    return ClassificationDataset.objects.create(
        name="Test Dataset",
        label_studio_url="http://label-studio:8080",
        label_studio_api_key="test-api-key",
        ml_backend_url="http://ml-backend:9090",
        batch_size=16,
        max_epochs=10,
        owner=user,
    )


@pytest.fixture
def label(dataset):
    return ClassificationLabel.objects.create(
        dataset=dataset,
        class_index=0,
        class_label="Cat",
    )


@pytest.fixture
def datapoint(dataset, label):
    test_file = SimpleUploadedFile(
        "test.jpg",
        b"file_content",
        content_type="image/jpeg",
    )
    return ClassificationDatapoint.objects.create(
        file=test_file,
        label=label,
        dataset=dataset,
    )


@pytest.mark.django_db
class TestClassificationDatasetAPI:
    def test_list_datasets(self, api_client, dataset, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/data/datasets/classification/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Dataset"

    def test_create_dataset(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {
            "name": "New Dataset",
            "label_studio_url": "http://localhost:8080",
            "label_studio_api_key": "key123",
            "ml_backend_url": "http://localhost:9090",
            "max_epochs": 5,
            "owner": user.id,
        }
        response = api_client.post("/api/data/datasets/classification/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Dataset"
        assert ClassificationDataset.objects.filter(name="New Dataset").exists()

    def test_retrieve_dataset(self, api_client, dataset, user):
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/data/datasets/classification/{dataset.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Dataset"
        assert response.data["id"] == dataset.id

    def test_update_dataset(self, api_client, dataset, user):
        api_client.force_authenticate(user=user)
        data = {
            "name": "Updated Dataset",
            "label_studio_url": dataset.label_studio_url,
            "label_studio_api_key": dataset.label_studio_api_key,
            "ml_backend_url": dataset.ml_backend_url,
            "max_epochs": dataset.max_epochs,
            "owner": user.id,
        }
        response = api_client.put(
            f"/api/data/datasets/classification/{dataset.id}/",
            data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Dataset"
        dataset.refresh_from_db()
        assert dataset.name == "Updated Dataset"

    def test_delete_dataset(self, api_client, dataset, user):
        api_client.force_authenticate(user=user)
        dataset_id = dataset.id
        response = api_client.delete(f"/api/data/datasets/classification/{dataset_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ClassificationDataset.objects.filter(id=dataset_id).exists()


@pytest.mark.django_db
class TestClassificationLabelAPI:
    def test_list_labels(self, api_client, label, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/data/labels/classification/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["class_label"] == "Cat"

    def test_create_label(self, api_client, dataset, user):
        api_client.force_authenticate(user=user)
        data = {
            "dataset": dataset.id,
            "class_index": 1,
            "class_label": "Dog",
        }
        response = api_client.post("/api/data/labels/classification/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["class_label"] == "Dog"
        assert ClassificationLabel.objects.filter(class_label="Dog").exists()

    def test_retrieve_label(self, api_client, label, user):
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/data/labels/classification/{label.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["class_label"] == "Cat"

    def test_delete_label(self, api_client, label, user):
        api_client.force_authenticate(user=user)
        label_id = label.id
        response = api_client.delete(f"/api/data/labels/classification/{label_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ClassificationLabel.objects.filter(id=label_id).exists()


@pytest.mark.django_db
class TestClassificationDatapointAPI:
    def test_list_datapoints(self, api_client, datapoint, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/data/datapoints/classification/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_datapoint_with_file(self, api_client, dataset, user):
        api_client.force_authenticate(user=user)
        test_file = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg",
        )
        data = {
            "file": test_file,
            "dataset": dataset.id,
        }
        response = api_client.post(
            "/api/data/datapoints/classification/",
            data,
            format="multipart",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert ClassificationDatapoint.objects.filter(dataset=dataset).count() == 1

    def test_create_datapoint_with_label(self, api_client, dataset, label, user):
        api_client.force_authenticate(user=user)
        test_file = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        data = {
            "file": test_file,
            "dataset": dataset.id,
            "class_index": label.class_index,
        }
        response = api_client.post(
            "/api/data/datapoints/classification/",
            data,
            format="multipart",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["label"]["class_label"] == "Cat"

    def test_retrieve_datapoint(self, api_client, datapoint, user):
        api_client.force_authenticate(user=user)
        response = api_client.get(
            f"/api/data/datapoints/classification/{datapoint.id}/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == datapoint.id
        assert "file_url" in response.data

    def test_delete_datapoint(self, api_client, datapoint, user):
        api_client.force_authenticate(user=user)
        datapoint_id = datapoint.id
        response = api_client.delete(
            f"/api/data/datapoints/classification/{datapoint_id}/",
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ClassificationDatapoint.objects.filter(id=datapoint_id).exists()


@pytest.mark.django_db
class TestClassificationPredictionAPI:
    def test_list_predictions(self, api_client, datapoint, label, user):
        api_client.force_authenticate(user=user)
        ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.95,
            model_version=1,
        )
        response = api_client.get("/api/data/predictions/classification/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_prediction(self, api_client, datapoint, label, user):
        api_client.force_authenticate(user=user)
        data = {
            "datapoint": datapoint.id,
            "predicted_class_index": label.class_index,
            "confidence": 0.92,
            "model_version": 1,
        }
        response = api_client.post("/api/data/predictions/classification/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["confidence"] == 0.92  # noqa: PLR2004
        assert response.data["predicted_label"]["class_label"] == "Cat"

    def test_create_prediction_invalid_class_index(self, api_client, datapoint, user):
        api_client.force_authenticate(user=user)
        data = {
            "datapoint": datapoint.id,
            "predicted_class_index": 999,
            "confidence": 0.92,
            "model_version": 1,
        }
        response = api_client.post("/api/data/predictions/classification/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_prediction(self, api_client, datapoint, label, user):
        api_client.force_authenticate(user=user)
        prediction = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.88,
            model_version=1,
        )
        response = api_client.get(
            f"/api/data/predictions/classification/{prediction.id}/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["confidence"] == 0.88  # noqa: PLR2004

    def test_update_prediction(self, api_client, datapoint, label, user):
        api_client.force_authenticate(user=user)
        prediction = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.8,
            model_version=1,
        )
        data = {
            "datapoint": datapoint.id,
            "predicted_class_index": label.class_index,
            "confidence": 0.95,
            "model_version": 1,
        }
        response = api_client.put(
            f"/api/data/predictions/classification/{prediction.id}/",
            data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["confidence"] == 0.95  # noqa: PLR2004
        prediction.refresh_from_db()
        assert prediction.confidence == 0.95  # noqa: PLR2004

    def test_delete_prediction(self, api_client, datapoint, label, user):
        api_client.force_authenticate(user=user)
        prediction = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.9,
            model_version=1,
        )
        prediction_id = prediction.id
        response = api_client.delete(
            f"/api/data/predictions/classification/{prediction_id}/",
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ClassificationPrediction.objects.filter(id=prediction_id).exists()
