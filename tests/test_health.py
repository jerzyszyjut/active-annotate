import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test cases for the health endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_200(self, client: AsyncClient):
        """Test that the health endpoint returns a 200 status code."""
        response = await client.get("/health")
        assert response.status_code == 200
