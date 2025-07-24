Testing with pytest
===================

This project uses `pytest <https://docs.pytest.org/>`_ for testing, along with `pytest-asyncio <https://pytest-asyncio.readthedocs.io/>`_ for testing asynchronous FastAPI endpoints.

Test Structure
--------------

The test suite is organized in the ``tests/`` directory with the following structure:

.. code-block::

   tests/
   ├── __init__.py
   ├── conftest.py          # Test configuration and fixtures
   └── test_health.py       # Health endpoint tests

Test Configuration
------------------

The testing setup is configured in ``tests/conftest.py``, which provides:

- **Async test client fixture** - Creates an HTTPX AsyncClient for testing FastAPI endpoints
- **Automatic cleanup** - Clears dependency overrides after each test

Key Components:

.. literalinclude:: ../tests/conftest.py
   :language: python
   :lines: 6-12

Running Tests
-------------

Docker Testing (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Docker for testing ensures consistent test environments:

.. code-block:: bash

   # Run all tests
   make test

   # Run tests with coverage report
   make test-cov

   # Run tests with Docker Compose directly
   docker compose -f docker-compose.dev.yml exec api-dev pytest

   # Run tests with verbose output
   docker compose -f docker-compose.dev.yml exec api-dev pytest -v

   # Run tests in a specific file
   docker compose -f docker-compose.dev.yml exec api-dev pytest tests/test_health.py

   # Run a specific test function
   docker compose -f docker-compose.dev.yml exec api-dev pytest tests/test_health.py::TestHealthEndpoint::test_health_endpoint_returns_200

Local Testing with Pipenv
~~~~~~~~~~~~~~~~~~~~~~~~~~

For local development setup:

.. code-block:: bash

   # Activate pipenv environment
   pipenv shell

   # Run all tests
   pipenv run pytest

   # Run tests with verbose output
   pipenv run pytest -v

   # Run tests in a specific file
   pipenv run pytest tests/test_health.py

   # Run a specific test function
   pipenv run pytest tests/test_health.py::TestHealthEndpoint::test_health_endpoint_returns_200

Test Output and Coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Docker testing with coverage:

.. code-block:: bash

   # Run tests with coverage (generates HTML, XML, and terminal reports)
   make test-cov

   # View coverage report in browser (after running test-cov)
   # Open htmlcov/index.html in your browser

Local testing with additional options:

.. code-block:: bash

   # Show print statements during tests
   pipenv run pytest -s

   # Show detailed test results
   pipenv run pytest -v

   # Stop after first failure
   pipenv run pytest -x

   # Run tests matching a pattern
   pipenv run pytest -k "health"

Async Testing
-------------

This project uses ``pytest-asyncio`` to handle asynchronous tests. All async test functions should be marked with ``@pytest.mark.asyncio``:

.. code-block:: python

   @pytest.mark.asyncio
   async def test_async_endpoint(self, client: AsyncClient):
       """Test an async endpoint."""
       response = await client.get("/some-endpoint")
       assert response.status_code == 200

Writing Tests
-------------

Test Class Organization
~~~~~~~~~~~~~~~~~~~~~~~

Tests are organized into classes that group related functionality:

.. literalinclude:: ../tests/test_health.py
   :language: python
   :lines: 5-12

Using the Test Client
~~~~~~~~~~~~~~~~~~~~~

The ``client`` fixture provides an HTTPX AsyncClient configured for testing:

.. code-block:: python

   @pytest.mark.asyncio
   async def test_api_endpoint(self, client: AsyncClient):
       # GET request
       response = await client.get("/api/endpoint")

       # POST request with JSON data
       response = await client.post("/api/create", json={"name": "test"})

       # Request with headers
       response = await client.get("/api/protected", headers={"Authorization": "Bearer token"})

       # Assertions
       assert response.status_code == 200
       assert response.json() == {"expected": "result"}

Test Examples
~~~~~~~~~~~~~

Here are common testing patterns for this FastAPI project:

**Testing JSON responses:**

.. code-block:: python

   @pytest.mark.asyncio
   async def test_json_response(self, client: AsyncClient):
       response = await client.get("/api/data")
       assert response.status_code == 200
       data = response.json()
       assert "key" in data
       assert data["key"] == "expected_value"

**Testing error responses:**

.. code-block:: python

   @pytest.mark.asyncio
   async def test_not_found(self, client: AsyncClient):
       response = await client.get("/api/nonexistent")
       assert response.status_code == 404

**Testing POST endpoints:**

.. code-block:: python

   @pytest.mark.asyncio
   async def test_create_resource(self, client: AsyncClient):
       payload = {"name": "test", "description": "Test resource"}
       response = await client.post("/api/resources", json=payload)
       assert response.status_code == 201
       created = response.json()
       assert created["name"] == payload["name"]

Best Practices
--------------

Test Organization
~~~~~~~~~~~~~~~~~

- **Group related tests** into classes with descriptive names
- **Use descriptive test method names** that explain what is being tested
- **Add docstrings** to test classes and methods for documentation

Test Data
~~~~~~~~~

- **Use fixtures** for reusable test data and setup
- **Keep test data minimal** - only include what's necessary for the test
- **Avoid hardcoded values** where possible - use variables or fixtures

Assertions
~~~~~~~~~~

- **Test one thing per test** - each test should verify a single behavior
- **Use specific assertions** - check exact values rather than just truthy/falsy
- **Test both success and failure cases** for each endpoint

Environment Isolation
~~~~~~~~~~~~~~~~~~~~~

- **Tests run in isolation** - the test client and fixtures ensure clean state
- **Dependencies are automatically cleared** after each test via ``conftest.py``
- **Use dependency overrides** for mocking external services if needed

Common Test Commands Summary
----------------------------

Docker Commands (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Basic testing
   make test                           # Run all tests
   make test-cov                       # Run tests with coverage report

   # Using Docker Compose directly
   docker compose -f docker-compose.dev.yml exec api-dev pytest                    # Run all tests
   docker compose -f docker-compose.dev.yml exec api-dev pytest -v                # Verbose output
   docker compose -f docker-compose.dev.yml exec api-dev pytest -s                # Show print statements
   docker compose -f docker-compose.dev.yml exec api-dev pytest -x                # Stop on first failure

   # Specific test selection
   docker compose -f docker-compose.dev.yml exec api-dev pytest tests/test_health.py                      # Run specific file
   docker compose -f docker-compose.dev.yml exec api-dev pytest -k "health"                               # Run tests matching pattern
   docker compose -f docker-compose.dev.yml exec api-dev pytest tests/test_health.py::TestHealthEndpoint  # Run specific class

Local Commands (Pipenv)
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Basic testing
   pipenv run pytest                    # Run all tests
   pipenv run pytest -v                # Verbose output
   pipenv run pytest -s                # Show print statements
   pipenv run pytest -x                # Stop on first failure

   # Specific test selection
   pipenv run pytest tests/test_health.py                      # Run specific file
   pipenv run pytest -k "health"                               # Run tests matching pattern
   pipenv run pytest tests/test_health.py::TestHealthEndpoint  # Run specific class

   # Output and reporting
   pipenv run pytest --tb=short        # Shorter traceback format
   pipenv run pytest --tb=no           # No traceback
   pipenv run pytest -q                # Quiet output
