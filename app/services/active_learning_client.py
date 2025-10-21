import heapq
import math
from pathlib import Path
from typing import Literal

from app.schemas.ml_backend import ALPredictResponse


class ActiveLearningClientService:

    def __init__(self, method:  Literal["least_confidence", "entropy", "margin"]):
        self.method = method

    def select_images(self, predictions: ALPredictResponse, al_batch: int) -> list[Path]:
        filenames = [prediction.filename for prediction in predictions.results]
        image_scores = [prediction.scores for prediction in predictions.results]
        if self.method == "least_confidence":
            data = [(filename, max(scores)) for filename, scores in zip(filenames, image_scores)]
            sorted_data = sorted(data, key=lambda x: x[1])[:min(al_batch, len(data))]
        elif self.method == "entropy":
            uncertainty = []
            for scores in image_scores:
                entropy = 0.0
                for score in scores:
                    class_entropy = -score * math.log2(score) if score > 0 else 0.0
                    entropy += class_entropy
                uncertainty.append(entropy)
            data = [(filename, inst_uncertainty) for filename, inst_uncertainty in zip(filenames, uncertainty)]
            sorted_data = sorted(data, key=lambda x: x[1], reverse=True)[:min(al_batch, len(data))]
        else:
            margins = []
            for scores in image_scores:
                top2 = heapq.nlargest(2, scores)
                margins.append(top2[0] - top2[1])
            data = [(filename, margin) for filename, margin in zip(filenames, margins)]
            sorted_data = sorted(data, key=lambda x: x[1])[:min(al_batch, len(data))]
        
        return [Path(image_path) for image_path, _ in sorted_data]