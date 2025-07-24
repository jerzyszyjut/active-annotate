.. Active Annotate documentation master file, created by
   sphinx-quickstart on Wed Jul 23 09:40:29 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Active Annotate Documentation
=============================

Welcome to the **Active Annotate** project documentation. This is a backend API for managing active learning annotation projects, built with FastAPI and modern Python development practices.

.. note::

   This project is under active development.

Project Overview
================

Active Annotate is designed to facilitate active learning workflows for data annotation projects. The API provides endpoints for managing annotation tasks, datasets, and machine learning model integration.

**Key Features:**

- **FastAPI Framework** - Modern, fast web framework for building APIs
- **Async Support** - Built for high-performance asynchronous operations
- **Type Safety** - Full type hints and validation with Pydantic
- **Developer Tools** - Pre-commit hooks, linting, and formatting with Ruff
- **Testing** - Comprehensive test suite with pytest and async testing support
- **Documentation** - Auto-generated docs with Sphinx

Quick Start
===========

Docker (Recommended)
~~~~~~~~~~~~~~~~~~~~~

1. **Start development environment:**

   .. code-block:: bash

      make up

2. **Run database migrations:**

   .. code-block:: bash

      make migrate

3. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

Alternative: Local Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Install dependencies:**

   .. code-block:: bash

      pipenv install --dev

2. **Activate environment:**

   .. code-block:: bash

      pipenv shell

3. **Run the application:**

   .. code-block:: bash

      pipenv run uvicorn app.main:app --reload

4. **Run tests:**

   .. code-block:: bash

      pipenv run pytest

Project Structure
=================

.. code-block::

   active-annotate/
   ├── app/                    # Application source code
   │   ├── main.py            # FastAPI application entry point
   │   ├── api/               # API routes and endpoints
   │   └── core/              # Core configuration and settings
   ├── tests/                 # Test suite
   │   ├── conftest.py        # Test configuration and fixtures
   │   └── test_*.py          # Test modules
   ├── docs/                  # Documentation source files
   ├── Pipfile               # Python dependencies
   └── pyproject.toml        # Project configuration

Documentation Sections
=======================

.. toctree::
   :maxdepth: 2
   :caption: Getting Started:

   installation
   docker
   development

.. toctree::
   :maxdepth: 2
   :caption: Development:

   testing
   documentation

.. toctree::
   :maxdepth: 2
   :caption: Reference:

   api

API Reference
=============

This project uses FastAPI's built-in OpenAPI documentation instead of maintaining separate API docs:

**Interactive Documentation:**
- **Swagger UI**: Start the app and visit ``http://localhost:8000/docs``
- **ReDoc**: Start the app and visit ``http://localhost:8000/redoc``

**Benefits:**
- Always up-to-date with the actual code
- Interactive testing interface
- Automatic schema generation
- Zero maintenance overhead

For application configuration and setup details, see the :doc:`api` section.

Contributing
============

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Run pre-commit hooks to ensure code quality
6. Submit a pull request

The project uses:

- **Pre-commit hooks** for code quality enforcement
- **Ruff** for linting and formatting
- **pytest** for testing
- **Type hints** throughout the codebase

License
=======

This project is under active development. License information will be added soon.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
