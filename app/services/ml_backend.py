# Temporary file, it'll be replaced by ml_backend component
import numpy as np


class MlBackendService:
    def __init__(self):
        pass

    def train(self, data):
        pass
    
    def predict(self, image_paths: list, num_of_classes: int):
        probs = [np.random.rand(num_of_classes) for _ in range(len(image_paths))]
        return [list(prob / prob.sum()) for prob in probs]




