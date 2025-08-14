


class ActiveLearningClientService:
    def __init__(self, annotated_data: dict):
        self.annotated_data = annotated_data

    def update_annotation(self, annotated_data_batch: dict) -> dict:
        self.annotated_data.update(annotated_data_batch)
        return self.annotated_data

    def select_images(self, image_paths: list, probabilities: list[list], al_batch: int):
        uncertainty = [max(image_probs) for image_probs in probabilities] 
        data = [data_sample for data_sample in zip(image_paths, uncertainty)]
        sorted_data = sorted(data, key=lambda x: x[1])[:min(al_batch, len(data))]
        
        return [image_path for image_path, _ in sorted_data]