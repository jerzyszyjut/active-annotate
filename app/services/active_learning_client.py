


class ActiveLearningClientService:
    def __init__(self, annotated_data: dict):
        self.annotated_data = annotated_data

    def update_annotation(self, annotated_data_batch: dict) -> dict:
        self.annotated_data.update(annotated_data_batch)
        return self.annotated_data

    def select_images(self, image_paths: list, predictions: list, al_batch: int):
        uncertainty = [abs(0.5 - pred) for pred in predictions] 
        data = [data_sample for data_sample in zip(image_paths, uncertainty)]
        sorted_data = sorted(data, key=lambda x: x[1])[:min(al_batch, len(data))]
        
        return [image_path for image_path, _ in sorted_data]