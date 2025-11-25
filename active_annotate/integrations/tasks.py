import time

import httpx
from celery import shared_task

from active_annotate.datasets.models import ClassificationDataset
from active_annotate.integrations.services import LabelStudioService
from active_annotate.integrations.services import MLBackendService

MAX_WAIT_SECONDS = 3600


@shared_task
def start_active_learning_loop(dataset_id: int) -> None:
    dataset = ClassificationDataset.objects.get(pk=dataset_id)
    ls_service = LabelStudioService(dataset)
    ls_service.create_active_learning_project()


@shared_task
def step_in_active_learning_loop(dataset_id: int, project_id: int) -> None:
    dataset = ClassificationDataset.objects.get(pk=dataset_id)
    backend_service = MLBackendService(dataset)

    backend_service.train_model()

    start_time = time.time()
    poll_interval = 5

    while time.time() - start_time < MAX_WAIT_SECONDS:
        try:
            status_data = backend_service.check_model_status()

            if status_data == "idle":
                break

        except httpx.HTTPError:
            pass

        time.sleep(poll_interval)

    backend_service.infer_predictions()

    ls_service = LabelStudioService(dataset)
    ls_service.delete_project(project_id)

    if ls_service.is_stop_condition_met():
        dataset.state = "finished"
        dataset.save()
    else:
        ls_service.create_active_learning_project()
