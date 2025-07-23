API Reference
=============

This section provides information about the Active Annotate API configuration and how to access the interactive API documentation.

Application Configuration
-------------------------

.. autoclass:: app.core.config.Settings
   :members:
   :undoc-members:
   :no-index:

Main Application Setup
----------------------

The FastAPI application is configured with the following features:

- **CORS middleware** for cross-origin requests (when configured)
- **Automatic OpenAPI schema generation**
- **Interactive documentation** via Swagger UI and ReDoc
- **Type validation** with Pydantic models

.. literalinclude:: ../app/main.py
   :language: python
   :lines: 11-25
   :caption: FastAPI application initialization

Interactive API Documentation
=============================

FastAPI automatically generates comprehensive, interactive API documentation. Instead of maintaining separate documentation for endpoints, use the built-in OpenAPI documentation:

Swagger UI
----------

The Swagger UI provides an interactive interface for exploring and testing API endpoints:

**URL:** ``http://localhost:8000/docs``

**Features:**
- Interactive endpoint testing
- Request/response schemas
- Parameter descriptions
- Authentication testing
- Example requests and responses

ReDoc
-----

ReDoc provides a clean, readable API reference:

**URL:** ``http://localhost:8000/redoc``

**Features:**
- Clean, organized layout
- Detailed request/response documentation
- Schema visualization
- Code examples in multiple languages

OpenAPI Schema
--------------

The raw OpenAPI schema is available at:

**URL:** ``http://localhost:8000/openapi.json``

This JSON schema can be used to:
- Generate client SDKs
- Import into API testing tools
- Integrate with other documentation systems
- Validate API contracts

Getting Started with API Documentation
--------------------------------------

1. **Start the application:**

   .. code-block:: bash

      pipenv run uvicorn app.main:app --reload

2. **Open Swagger UI in your browser:**

   Navigate to ``http://localhost:8000/docs``

3. **Explore the endpoints:**

   - Click on any endpoint to see details
   - Use "Try it out" to test endpoints
   - View request/response schemas
   - See example data

4. **For detailed reference:**

   Visit ``http://localhost:8000/redoc`` for a comprehensive reference view

Why Use OpenAPI Documentation?
------------------------------

**Advantages:**

- **Always up-to-date** - Generated directly from code
- **Interactive testing** - Test endpoints without additional tools
- **Type-safe** - Reflects actual Pydantic models and type hints
- **Standard format** - Uses OpenAPI 3.0 specification
- **Zero maintenance** - No manual documentation updates needed
- **Client generation** - Can generate SDKs for various languages

**Best Practices:**

- Add comprehensive docstrings to your endpoint functions
- Use Pydantic models for request/response schemas
- Include response examples in your endpoint definitions
- Document error responses with appropriate status codes
