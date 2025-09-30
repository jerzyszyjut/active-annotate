from pathlib import Path

from app.schemas.ml_backend import PredictResponse


class ActiveLearningClientService:

    def select_images(self, predictions: PredictResponse, al_batch: int) -> list[Path]:
        data = [[prediction[0].filename, prediction[0].score] for prediction in predictions.results]
        sorted_data = sorted(data, key=lambda x: x[1])[:min(al_batch, len(data))]
        return [Path(image_path) for image_path, _ in sorted_data]