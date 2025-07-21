import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Test creating a new project."""
    project_data = {
        "name": "Test Project",
        "active_learning_batch_size": 20,
        "description": "Test project description"
    }
    
    response = await client.post("/api/v1/projects/", json=project_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["active_learning_batch_size"] == project_data["active_learning_batch_size"]
    assert data["description"] == project_data["description"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_projects(client: AsyncClient, session: AsyncSession):
    """Test getting all projects."""
    # Create test projects
    project1 = Project(name="Project 1", active_learning_batch_size=10)
    project2 = Project(name="Project 2", active_learning_batch_size=15)
    
    session.add(project1)
    session.add(project2)
    await session.commit()
    
    response = await client.get("/api/v1/projects/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Project 1"
    assert data[1]["name"] == "Project 2"


@pytest.mark.asyncio
async def test_get_project_by_id(client: AsyncClient, session: AsyncSession):
    """Test getting a project by ID."""
    project = Project(name="Test Project", active_learning_batch_size=10)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    response = await client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == project.id
    assert data["name"] == project.name


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, session: AsyncSession):
    """Test updating a project."""
    project = Project(name="Original Project", active_learning_batch_size=10)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    update_data = {
        "name": "Updated Project",
        "active_learning_batch_size": 25
    }
    
    response = await client.put(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["active_learning_batch_size"] == update_data["active_learning_batch_size"]


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, session: AsyncSession):
    """Test deleting a project."""
    project = Project(name="Project to Delete", active_learning_batch_size=10)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    response = await client.delete(f"/api/v1/projects/{project.id}")
    assert response.status_code == 204
    
    # Verify project is deleted
    response = await client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_project(client: AsyncClient):
    """Test getting a non-existent project."""
    response = await client.get("/api/v1/projects/999")
    assert response.status_code == 404
