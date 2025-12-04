import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.datasets.models import ClassificationLabel
from active_annotate.datasets.models import ClassificationPrediction
from active_annotate.integrations.models import LabelStudioIntegration

User = get_user_model()


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
        uncertainty_strategy="entropy",
        epoch=0,
        max_epochs=10,
        state="not-started",
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
class TestClassificationDataset:
    def test_create_dataset(self, user):
        dataset = ClassificationDataset.objects.create(
            name="New Dataset",
            label_studio_url="http://localhost:8080",
            label_studio_api_key="key123",
            ml_backend_url="http://localhost:9090",
            max_epochs=5,
            owner=user,
        )
        assert dataset.name == "New Dataset"
        assert dataset.epoch == 0
        assert dataset.state == "not-started"
        assert dataset.batch_size == 16  # noqa: PLR2004

    def test_dataset_str(self, dataset):
        assert str(dataset) == "Test Dataset"

    def test_dataset_owner_relationship(self, user, dataset):
        assert dataset.owner == user
        assert dataset in user.datasets.all()


@pytest.mark.django_db
class TestClassificationLabel:
    def test_create_label(self, dataset):
        label = ClassificationLabel.objects.create(
            dataset=dataset,
            class_index=1,
            class_label="Dog",
        )
        assert label.class_index == 1
        assert label.class_label == "Dog"
        assert label.dataset == dataset

    def test_label_str(self, label):
        expected = "Test Dataset - Cat (ID: 0)"
        assert str(label) == expected

    def test_unique_constraint(self, dataset, label):
        with pytest.raises(IntegrityError):
            ClassificationLabel.objects.create(
                dataset=dataset,
                class_index=0,
                class_label="Another Cat",
            )

    def test_multiple_labels_same_dataset(self, dataset):
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
        assert dataset.labels.count() == 2  # noqa: PLR2004
        assert label1 in dataset.labels.all()
        assert label2 in dataset.labels.all()


@pytest.mark.django_db
class TestClassificationDatapoint:
    def test_create_datapoint(self, dataset):
        test_file = SimpleUploadedFile(
            "image.jpg",
            b"content",
            content_type="image/jpeg",
        )
        datapoint = ClassificationDatapoint.objects.create(
            file=test_file,
            dataset=dataset,
        )
        assert datapoint.dataset == dataset
        assert datapoint.label is None
        assert datapoint.file.name

    def test_datapoint_with_label(self, datapoint, label):
        assert datapoint.label == label
        assert datapoint in label.datapoints.all()

    def test_datapoint_str(self, datapoint):
        expected = f"Datapoint {datapoint.pk} in Test Dataset"
        assert str(datapoint) == expected

    def test_datapoint_cascade_delete(self, dataset):
        test_file = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        datapoint = ClassificationDatapoint.objects.create(
            file=test_file,
            dataset=dataset,
        )
        datapoint_id = datapoint.pk
        dataset.delete()
        assert not ClassificationDatapoint.objects.filter(pk=datapoint_id).exists()

    def test_without_predictions_queryset(self, datapoint):
        version = 1
        queryset = ClassificationDatapoint.objects.without_predictions_for_version(
            version,
        )
        assert datapoint in queryset

        ClassificationPrediction.objects.create(
            datapoint=datapoint,
            model_version=version,
        )
        queryset = ClassificationDatapoint.objects.without_predictions_for_version(
            version,
        )
        assert datapoint not in queryset


@pytest.mark.django_db
class TestClassificationPrediction:
    def test_create_prediction(self, datapoint, label):
        prediction = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.95,
            model_version=1,
        )
        assert prediction.datapoint == datapoint
        assert prediction.predicted_label == label
        assert prediction.confidence == 0.95  # noqa: PLR2004
        assert prediction.model_version == 1

    def test_prediction_str(self, datapoint, label):
        prediction = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.85,
            model_version=1,
        )
        expected = (
            f"Prediction for Datapoint {datapoint.pk} - "
            f"Predicted: {label} (Confidence: 0.85)"
        )
        assert str(prediction) == expected

    def test_prediction_without_label(self, datapoint):
        prediction = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            model_version=1,
        )
        assert prediction.predicted_label is None
        assert prediction.confidence is None

    def test_multiple_predictions_same_datapoint(self, datapoint, label):
        pred1 = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.8,
            model_version=1,
        )
        pred2 = ClassificationPrediction.objects.create(
            datapoint=datapoint,
            predicted_label=label,
            confidence=0.9,
            model_version=2,
        )
        assert datapoint.predictions.count() == 2  # noqa: PLR2004
        assert pred1 in datapoint.predictions.all()
        assert pred2 in datapoint.predictions.all()


@pytest.mark.django_db
class TestLabelStudioIntegration:
    def test_create_integration(self):
        integration = LabelStudioIntegration.objects.create(
            url="http://localhost:8080",
            api_key="test-key-123",
            ml_backend_url="http://localhost:9090",
        )
        assert integration.url == "http://localhost:8080"
        assert integration.api_key == "test-key-123"
        assert integration.ml_backend_url == "http://localhost:9090"

    def test_integration_str(self):
        integration = LabelStudioIntegration.objects.create(
            url="http://example.com",
            api_key="key",
        )
        expected = "LabelStudio Integration - http://example.com"
        assert str(integration) == expected

    def test_integration_without_ml_backend(self):
        integration = LabelStudioIntegration.objects.create(
            url="http://localhost:8080",
            api_key="key123",
        )
        assert integration.ml_backend_url == ""
