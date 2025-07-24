"""Test cases for project endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.project import Project


# Test project data
TEST_PROJECT_DATA = {
    "name": "Test Project",
    "description": "A test project description",
    "active_learning_batch_size": 25,
}

TEST_PROJECT_UPDATE_DATA = {
    "name": "Updated Test Project",
    "description": "Updated description",
    "active_learning_batch_size": 30,
}


class TestProjectEndpoints:
    """Test cases for project CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_project_success(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test successful project creation."""
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "active_learning_batch_size": 100,
        }

        response = client.post("/projects/", json=project_data)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == project_data["name"]
        assert response_data["description"] == project_data["description"]
        assert (
            response_data["active_learning_batch_size"]
            == project_data["active_learning_batch_size"]
        )
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data

        # Verify project is in database
        result = await test_session.execute(
            select(Project).where(Project.id == response_data["id"])
        )
        db_project = result.scalar_one_or_none()
        assert db_project is not None
        assert db_project.name == project_data["name"]

    @pytest.mark.asyncio
    async def test_get_projects_empty_list(self, client: TestClient):
        """Test getting projects when none exist."""
        response = client.get("/projects/")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_projects_with_data(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test getting projects with existing data."""
        # Create a project in the database
        project = Project(**TEST_PROJECT_DATA)
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        response = client.get("/projects/")

        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 1
        assert projects[0]["name"] == TEST_PROJECT_DATA["name"]
        assert projects[0]["id"] == project.id

    @pytest.mark.asyncio
    async def test_get_projects_with_pagination(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test getting projects with pagination parameters."""
        # Create multiple projects
        for i in range(15):
            project = Project(
                name=f"Project {i}",
                description=f"Description {i}",
                active_learning_batch_size=10,
            )
            test_session.add(project)
        await test_session.commit()

        response = client.get("/projects/?skip=10&limit=5")

        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 5

    @pytest.mark.asyncio
    async def test_get_project_by_id_success(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test getting a specific project by ID."""
        # Create a project in the database
        project = Project(**TEST_PROJECT_DATA)
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        response = client.get(f"/projects/{project.id}")

        assert response.status_code == 200
        project_data = response.json()
        assert project_data["id"] == project.id
        assert project_data["name"] == TEST_PROJECT_DATA["name"]

    @pytest.mark.asyncio
    async def test_get_project_by_id_not_found(self, client: TestClient):
        """Test getting a project that doesn't exist."""
        response = client.get("/projects/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project not found"

    @pytest.mark.asyncio
    async def test_update_project_success(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test successful project update."""
        # Create a project in the database
        project = Project(**TEST_PROJECT_DATA)
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        response = client.put(f"/projects/{project.id}", json=TEST_PROJECT_UPDATE_DATA)

        assert response.status_code == 200
        project_data = response.json()
        assert project_data["id"] == project.id
        assert project_data["name"] == TEST_PROJECT_UPDATE_DATA["name"]
        assert project_data["description"] == TEST_PROJECT_UPDATE_DATA["description"]

        # Verify the project was actually updated in the database
        await test_session.refresh(project)
        assert project.name == TEST_PROJECT_UPDATE_DATA["name"]
        assert project.description == TEST_PROJECT_UPDATE_DATA["description"]

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, client: TestClient):
        """Test updating a project that doesn't exist."""
        response = client.put("/projects/999", json=TEST_PROJECT_UPDATE_DATA)

        assert response.status_code == 404
        assert response.json()["detail"] == "Project not found"

    @pytest.mark.asyncio
    async def test_update_project_partial(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test partial project update."""
        # Create a project in the database
        project = Project(**TEST_PROJECT_DATA)
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        # Only update name
        partial_update = {"name": "Partially Updated Project"}

        response = client.put(f"/projects/{project.id}", json=partial_update)

        assert response.status_code == 200
        project_data = response.json()
        assert project_data["name"] == "Partially Updated Project"
        assert (
            project_data["description"] == TEST_PROJECT_DATA["description"]
        )  # Should remain unchanged

        # Verify the project was actually updated in the database
        await test_session.refresh(project)
        assert project.name == "Partially Updated Project"
        assert project.description == TEST_PROJECT_DATA["description"]

    @pytest.mark.asyncio
    async def test_delete_project_success(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test successful project deletion."""
        # Create a project in the database
        project = Project(**TEST_PROJECT_DATA)
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)
        project_id = project.id

        response = client.delete(f"/projects/{project_id}")

        assert response.status_code == 204
        assert response.content == b""

        # Verify deletion by trying to get the project via API (which uses the same session factory)
        get_response = client.get(f"/projects/{project_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, client: TestClient):
        """Test deleting a project that doesn't exist."""
        response = client.delete("/projects/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project not found"

    @pytest.mark.asyncio
    async def test_create_project_validation_error(self, client: TestClient):
        """Test project creation with validation errors."""
        invalid_project_data = {
            "name": "",  # Empty name should fail validation
            "active_learning_batch_size": 0,  # Should be >= 1
        }

        response = client.post("/projects/", json=invalid_project_data)

        assert response.status_code == 422
        error_details = response.json()["detail"]

        # Check that validation errors are present
        assert any("name" in str(error) for error in error_details)
        assert any(
            "active_learning_batch_size" in str(error) for error in error_details
        )

    @pytest.mark.asyncio
    async def test_create_project_name_too_long(self, client: TestClient):
        """Test project creation with name exceeding max length."""
        invalid_project_data = {
            "name": "x" * 201,  # Exceeds max_length=200
            "active_learning_batch_size": 10,
        }

        response = client.post("/projects/", json=invalid_project_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_batch_size_too_large(self, client: TestClient):
        """Test project creation with batch size exceeding limit."""
        invalid_project_data = {
            "name": "Valid Name",
            "active_learning_batch_size": 1001,  # Exceeds le=1000
        }

        response = client.post("/projects/", json=invalid_project_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_project_validation_error(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test project update with validation errors."""
        # Create a project in the database
        project = Project(**TEST_PROJECT_DATA)
        test_session.add(project)
        await test_session.commit()
        await test_session.refresh(project)

        invalid_update_data = {
            "name": "",  # Empty name should fail validation
            "active_learning_batch_size": 0,  # Should be >= 1
        }

        response = client.put(f"/projects/{project.id}", json=invalid_update_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_minimal_data(self, client: TestClient):
        """Test creating a project with minimal required data."""
        minimal_project_data = {
            "name": "Minimal Project",
        }

        response = client.post("/projects/", json=minimal_project_data)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == "Minimal Project"
        assert response_data["description"] is None
        assert response_data["active_learning_batch_size"] == 10  # Default value

    @pytest.mark.asyncio
    async def test_get_projects_ordering(
        self, client: TestClient, test_session: AsyncSession
    ):
        """Test that projects are returned in a consistent order."""
        # Create multiple projects
        project_names = ["Project A", "Project B", "Project C"]
        for name in project_names:
            project = Project(
                name=name,
                description=f"Description for {name}",
                active_learning_batch_size=10,
            )
            test_session.add(project)
        await test_session.commit()

        response = client.get("/projects/")

        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 3

        # Projects should be ordered consistently (likely by ID/creation order)
        returned_names = [p["name"] for p in projects]
        assert returned_names == project_names
