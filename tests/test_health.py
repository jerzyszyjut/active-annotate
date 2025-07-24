from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test cases for the health endpoint."""

    def test_health_endpoint_returns_200(self, client: TestClient):
        """Test that the health endpoint returns a 200 status code."""
        response = client.get("/health")
        assert response.status_code == 200
