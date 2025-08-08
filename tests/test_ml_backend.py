"""Tests for ML Backend API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.models.ml_backend import ModelResponse, PredictionValue

client = TestClient(app)


class TestMLBackendEndpoints:
    """Test cases for ML Backend API endpoints."""

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        with patch(
            "app.services.ml_backend.ml_backend_service.health_check"
        ) as mock_health:
            mock_health.return_value = {"status": "UP", "model_class": "TestModel"}

            response = client.get("/ml/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "UP"
            assert data["model_class"] == "TestModel"

    def test_root_endpoint(self):
        """Test the root ML endpoint."""
        with patch(
            "app.services.ml_backend.ml_backend_service.health_check"
        ) as mock_health:
            mock_health.return_value = {"status": "UP"}

            response = client.get("/ml/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "endpoints" in data
            assert "/ml/predict" in data["endpoints"]

    def test_setup_endpoint(self):
        """Test the setup endpoint."""
        setup_request = {
            "project": "1.1640995200",
            "label_config": "<View><Image name='image' value='$image'/></View>",
            "extra_params": {"model_type": "image_classifier"},
        }

        with patch("app.services.ml_backend.ml_backend_service.setup") as mock_setup:
            mock_setup.return_value = {"model_version": "1.0.0"}

            response = client.post("/ml/setup", json=setup_request)
            assert response.status_code == 200
            data = response.json()
            assert data["model_version"] == "1.0.0"

    def test_predict_endpoint(self):
        """Test the predict endpoint."""
        predict_request = {
            "tasks": [{"id": 1, "data": {"image": "https://example.com/image1.jpg"}}],
            "model_version": "1.0.0",
            "project": "1.1640995200",
            "label_config": "<View><Image name='image' value='$image'/></View>",
            "params": {"context": {}},
        }

        # Mock prediction response
        mock_prediction = PredictionValue(
            result=[
                {
                    "value": {"choices": ["cat"]},
                    "from_name": "choice",
                    "to_name": "image",
                    "type": "choices",
                }
            ],
            score=0.95,
            model_version="1.0.0",
        )

        mock_response = ModelResponse(
            model_version="1.0.0", predictions=[[mock_prediction]]
        )

        with patch(
            "app.services.ml_backend.ml_backend_service.predict"
        ) as mock_predict:
            mock_predict.return_value = mock_response

            response = client.post("/ml/predict", json=predict_request)
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) == 1

    def test_train_endpoint(self):
        """Test the train endpoint."""
        train_request = {
            "project_id": "1",
            "label_config": "<View><Image name='image' value='$image'/></View>",
            "use_ground_truth": True,
            "extra_params": {"epochs": 10},
        }

        with patch(
            "app.services.ml_backend.ml_backend_service.train_model"
        ) as mock_train:
            mock_train.return_value = {
                "status": "started",
                "message": "Training initiated successfully",
                "task_id": "train_123",
            }

            response = client.post("/ml/train", json=train_request)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "started"
            assert data["message"] == "Training initiated successfully"
            assert data["task_id"] == "train_123"

    def test_metrics_endpoint(self):
        """Test the metrics endpoint."""
        response = client.get("/ml/metrics")
        assert response.status_code == 200
        data = response.json()
        # Should return empty dict for now
        assert isinstance(data, dict)

    def test_predict_endpoint_error_handling(self):
        """Test error handling in predict endpoint."""
        predict_request = {
            "tasks": [{"id": 1, "data": {"image": "https://example.com/image1.jpg"}}]
        }

        with patch(
            "app.services.ml_backend.ml_backend_service.predict"
        ) as mock_predict:
            mock_predict.side_effect = Exception("ML Backend Error")

            response = client.post("/ml/predict", json=predict_request)
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Prediction failed" in data["detail"]

    def test_setup_endpoint_missing_project(self):
        """Test setup endpoint with missing project ID."""
        setup_request = {"project": "", "label_config": "<View></View>"}

        response = client.post("/ml/setup", json=setup_request)
        assert response.status_code == 400
        data = response.json()
        assert "Project ID is required" in data["detail"]

    def test_train_endpoint_error_handling(self):
        """Test error handling in train endpoint."""
        train_request = {"project_id": "1", "label_config": "<View></View>"}

        with patch(
            "app.services.ml_backend.ml_backend_service.train_model"
        ) as mock_train:
            mock_train.side_effect = Exception("Training Error")

            response = client.post("/ml/train", json=train_request)
            assert response.status_code == 200  # Returns 200 with error status
            data = response.json()
            assert data["status"] == "error"
            assert "Training failed" in data["message"]


if __name__ == "__main__":
    pytest.main([__file__])
