import io
import shutil
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
from celery import shared_task
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse

from active_annotate.datasets.models import ClassificationDatapoint
from active_annotate.datasets.models import ClassificationDataset
from active_annotate.integrations.services import LabelStudioService
from active_annotate.integrations.services import MLBackendService


@shared_task
def start_active_learning_loop(dataset_id: int, base_url: str):
    dataset = ClassificationDataset.objects.get(pk=dataset_id)
    ml_backend_service = MLBackendService(dataset)
    ml_backend_service.infer_predictions()

    parsed = urlparse(base_url)
    request = HttpRequest()
    request.META["HTTP_HOST"] = parsed.netloc
    request.META["wsgi.url_scheme"] = parsed.scheme

    label_studio_service = LabelStudioService(dataset, request=request)
    webhook_url = request.build_absolute_uri(
        reverse("integrations:label-studio-annotations-webhook"),
    )
    label_studio_service.create_active_learning_project(
        webhook_url=webhook_url,
        dataset_pk=dataset_id,
    )


@shared_task(bind=True)
def retrain_model_and_create_new_project(self, dataset_id: int, project_id: int):
    dataset = ClassificationDataset.objects.get(pk=dataset_id)
    ml_backend_service = MLBackendService(dataset)

    labeled_datapoints = ClassificationDatapoint.objects.filter(
        dataset=dataset,
        label__isnull=False,
    )

    if not labeled_datapoints.exists():
        return

    training_zip_bytes = _prepare_training_data(labeled_datapoints)

    if not training_zip_bytes:
        return

    try:
        response = httpx.post(
            f"{dataset.ml_backend_url}/train",
            files={
                "file": (
                    "training_data.zip",
                    io.BytesIO(training_zip_bytes),
                    "application/zip",
                ),
            },
            timeout=30.0,
        )
        response.raise_for_status()
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        raise self.retry(exc=e, countdown=10, max_retries=3) from e

    _wait_for_training_completion(ml_backend_service)
    ml_backend_service.infer_predictions()

    request = HttpRequest()
    allowed_host = (
        settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "django.django"
    )
    request.META["HTTP_HOST"] = allowed_host
    request.META["wsgi.url_scheme"] = "http"

    label_studio_service = LabelStudioService(dataset, request=request)
    webhook_url = request.build_absolute_uri(
        reverse("integrations:label-studio-annotations-webhook"),
    )
    label_studio_service.create_active_learning_project(
        webhook_url=webhook_url,
        dataset_pk=dataset_id,
    )


def _prepare_training_data(labeled_datapoints):
    temp_dir = tempfile.mkdtemp()
    try:
        temp_path = Path(temp_dir)

        class_counts = {}
        for dp in labeled_datapoints:
            class_label = dp.label.class_label
            if class_label not in class_counts:
                class_counts[class_label] = []
            class_counts[class_label].append(dp)

        if not class_counts:
            return None

        for class_label, datapoints in class_counts.items():
            train_dir = temp_path / "train" / class_label
            val_dir = temp_path / "val" / class_label
            train_dir.mkdir(parents=True, exist_ok=True)
            val_dir.mkdir(parents=True, exist_ok=True)

            split_idx = int(len(datapoints) * 0.8)
            train_datapoints = datapoints[:split_idx]
            val_datapoints = datapoints[split_idx:]

            for dp in train_datapoints:
                file_content = dp.file.read()
                file_ext = Path(dp.file.name).suffix or ".jpg"
                dest_path = train_dir / f"{dp.id}{file_ext}"
                dest_path.write_bytes(file_content)

            for dp in val_datapoints:
                file_content = dp.file.read()
                file_ext = Path(dp.file.name).suffix or ".jpg"
                dest_path = val_dir / f"{dp.id}{file_ext}"
                dest_path.write_bytes(file_content)

        shutil.make_archive(
            str(temp_path / "training_data"),
            "zip",
            temp_path,
        )
        zip_path = temp_path / "training_data.zip"
        return zip_path.read_bytes()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def _wait_for_training_completion(ml_backend_service, max_wait_seconds=3600):
    start_time = time.time()
    poll_interval = 5

    while time.time() - start_time < max_wait_seconds:
        try:
            response = httpx.get(f"{ml_backend_service.client.base_url}/status")
            status_data = response.json()

            if status_data["status"] == "idle":
                return

        except httpx.HTTPError:
            pass

        time.sleep(poll_interval)

    msg = "Training did not complete within the expected time"
    raise TimeoutError(msg)
