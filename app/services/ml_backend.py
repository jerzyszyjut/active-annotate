# Temporary file, it'll be replaced by ml_backend component
import random


class MlBackendService:
    def __init__(self):
        pass

    def train(self, data):
        pass
    
    def predict(self, image_paths: list):
        return [random.uniform(0, 1) for _ in range(len(image_paths))]




