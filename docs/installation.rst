Installation and Setup
======================

Docker Setup (Recommended)
---------------------------

This project uses Docker for streamlined development and deployment. This is the recommended approach for getting started quickly.

Prerequisites
~~~~~~~~~~~~~

Make sure you have Docker and Docker Compose installed on your system:

.. code-block:: bash

   # Verify Docker installation
   docker --version
   docker compose --version

Quick Start
~~~~~~~~~~~

1. **Clone the repository and navigate to the project directory**

2. **Start the development environment:**

.. code-block:: bash

   # Using Make (recommended)
   make up

   # Or using Docker Compose directly
   docker compose -f docker-compose.dev.yml up -d

3. **Run database migrations:**

.. code-block:: bash

   # Using Make
   make migrate

   # Or using Docker Compose directly
   docker compose -f docker-compose.dev.yml exec api-dev alembic upgrade head

4. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Interactive API Docs: http://localhost:8000/redoc

Available Make Commands
~~~~~~~~~~~~~~~~~~~~~~~

The project includes a comprehensive Makefile for common development tasks:

.. code-block:: bash

   # Start development environment
   make up

   # Stop environment
   make down

   # View logs
   make logs
   make logs-api    # API service logs only
   make logs-db     # Database logs only

   # Access container shells
   make shell       # API container
   make shell-db    # Database container

   # Run tests
   make test        # Run tests
   make test-cov    # Run tests with coverage

   # Database operations
   make migrate     # Run migrations
   make migration MSG="description"  # Create new migration
   make reset-db    # Reset database

   # Code quality
   make format      # Format code with Ruff
   make lint        # Lint code with Ruff
   make typecheck   # Run Pyright type checking

   # Cleanup
   make clean       # Remove all containers and images

Alternative: Local Python Environment with Pipenv
--------------------------------------------------

If you prefer local development without Docker, you can still use pipenv:

Prerequisites
~~~~~~~~~~~~~

Make sure you have Python 3.12 and pipenv installed on your system:

.. code-block:: bash

   # Install pipenv if you don't have it
   pipx install pipenv

   # Verify Python version
   python --version

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

1. Clone the repository and navigate to the project directory
2. Install all dependencies using pipenv:

.. code-block:: bash

   # Install dependencies from Pipfile
   pipenv install --dev

3. Activate the virtual environment:

.. code-block:: bash

   # Activate the pipenv shell
   pipenv shell

   # Or run commands in the environment without activating
   pipenv run <command>

Setting Up Type Checking (Required)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The project uses Pyright for type checking. You need to configure it for your local environment:

1. **Create the Pyright configuration file:**

.. code-block:: bash

   # Copy the example configuration
   cp pyrightconfig.json.example pyrightconfig.json

2. **Find your virtual environment path:**

.. code-block:: bash

   # Get the full path to your virtual environment
   pipenv --venv

3. **Update the configuration:**

   Edit ``pyrightconfig.json`` with your virtual environment details:

.. code-block:: json

   {
     "venvPath": "/your/virtualenvs/path",
     "venv": "your-venv-name"
   }

   Example:

.. code-block:: json

   {
     "venvPath": "/home/username/.local/share/virtualenvs",
     "venv": "active-annotate-bV0oe5Rx"
   }

**Important**: This file is required for the development tools to work properly and is gitignored since paths vary between systems.

Setting Up Development Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install and configure the pre-commit hooks:

.. code-block:: bash

   # Install pre-commit hooks
   pipenv run pre-commit install

   # Test the setup (optional)
   pipenv run pre-commit run --all-files
