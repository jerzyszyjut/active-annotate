Development Environment
=======================

Docker Development (Recommended)
---------------------------------

The recommended development approach uses Docker for consistency and ease of setup. All development tools and commands are available through the Makefile.

Quick Development Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Start the development environment:**

.. code-block:: bash

   make up

2. **Make code changes** (files are mounted as volumes, so changes are reflected immediately)

3. **Run tests:**

.. code-block:: bash

   make test

4. **Check code quality:**

.. code-block:: bash

   make lint      # Check for linting issues
   make format    # Format code
   make typecheck # Run type checking

5. **Create database migrations when needed:**

.. code-block:: bash

   make migration MSG="Add new table"
   make migrate

Available Development Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Environment management
   make up          # Start development environment
   make down        # Stop environment
   make logs        # View all logs
   make logs-api    # View API logs only
   make logs-db     # View database logs only

   # Container access
   make shell       # Access API container shell
   make shell-db    # Access database shell

   # Testing
   make test        # Run tests
   make test-cov    # Run tests with coverage report

   # Code quality
   make format      # Format code with Ruff
   make lint        # Lint code with Ruff
   make typecheck   # Run Pyright type checking

   # Database operations
   make migrate     # Run database migrations
   make migration MSG="description"  # Create new migration
   make reset-db    # Reset database (removes all data)

   # Cleanup
   make clean       # Remove all containers, volumes and images

Local Development with Pipenv
------------------------------

If you prefer local development without Docker, you can still use pipenv.

Setting up Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses pre-commit hooks to maintain code quality. Set them up after installing dependencies:

Installing Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Make sure you're in the activated pipenv environment:

.. code-block:: bash

   pipenv shell

2. Install the pre-commit hooks:

.. code-block:: bash

   pre-commit install

3. (Optional) Run pre-commit on all files to check the setup:

.. code-block:: bash

   pre-commit run --all-files

What Pre-commit Does
~~~~~~~~~~~~~~~~~~~~

Pre-commit hooks will automatically run before each commit to:

- **Trailing whitespace removal** - Removes unnecessary whitespace at line ends
- **End-of-file fixing** - Ensures files end with a newline
- **YAML validation** - Checks YAML files for syntax errors
- **Large file detection** - Prevents accidentally committing large files
- **Python linting and formatting** - Uses Ruff for code quality (see below)

If any hooks fail, the commit will be blocked until you fix the issues.

Code Quality with Ruff
-----------------------

This project uses `Ruff <https://docs.astral.sh/ruff/>`_ for Python linting and code formatting. Ruff is an extremely fast Python linter and code formatter written in Rust.

What Ruff Does
~~~~~~~~~~~~~~

Ruff performs two main functions:

1. **Linting** - Identifies code quality issues, potential bugs, and style violations
2. **Formatting** - Automatically formats code to maintain consistent style

Running Ruff (Docker)
~~~~~~~~~~~~~~~~~~~~~~

With Docker (recommended):

.. code-block:: bash

   # Format all Python files
   make format

   # Run linting checks
   make lint

Running Ruff (Local)
~~~~~~~~~~~~~~~~~~~~~

For local development with pipenv:

.. code-block:: bash

   # Activate pipenv environment
   pipenv shell

   # Run linting on all Python files
   pipenv run ruff check .

   # Run linting with automatic fixes
   pipenv run ruff check . --fix

   # Format all Python files
   pipenv run ruff format .

   # Check specific files or directories
   pipenv run ruff check src/
   pipenv run ruff format src/

Ruff Configuration
~~~~~~~~~~~~~~~~~~

Ruff is configured through the pre-commit hooks in ``.pre-commit-config.yaml``:

- **ruff check** - Runs linting with ``--fix`` to automatically fix issues when possible
- **ruff format** - Formats Python code according to style guidelines

The hooks run on Python files (``.py``) and Python interface files (``.pyi``).

Common Ruff Commands
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check for issues without fixing
   pipenv run ruff check .

   # Fix all auto-fixable issues
   pipenv run ruff check . --fix

   # Format code
   pipenv run ruff format .

   # Check and format in one go
   pipenv run ruff check . --fix && pipenv run ruff format .

   # Show what would be changed without making changes
   pipenv run ruff format . --diff

Integration with Pre-commit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you commit code, Ruff will automatically:

1. Run linting checks and apply automatic fixes
2. Format your code according to project standards
3. Fail the commit if there are issues that can't be auto-fixed

This ensures all committed code maintains consistent quality and style.

Type Checking with Pyright
---------------------------

This project uses `Pyright <https://microsoft.github.io/pyright/>`_ for static type checking. Pyright helps catch type-related bugs early and ensures code quality through static analysis.

Running Pyright (Docker)
~~~~~~~~~~~~~~~~~~~~~~~~~

With Docker (recommended):

.. code-block:: bash

   # Run type checking
   make typecheck

Running Pyright (Local)
~~~~~~~~~~~~~~~~~~~~~~~~

For local development with pipenv, you need to set up a configuration file first.

Setting Up Pyright Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Important**: You need to create a local ``pyrightconfig.json`` file for Pyright to work correctly with your virtual environment.

1. Create the configuration file in the project root:

.. code-block:: bash

   cp pyrightconfig.json.example pyrightconfig.json

2. Update the virtual environment path in ``pyrightconfig.json``:

.. code-block:: json

   {
     "venvPath": "/path/to/your/virtualenvs",
     "venv": "your-venv-name"
   }

3. Find your actual virtual environment path:

.. code-block:: bash

   # Show the virtual environment path
   pipenv --venv

   # The path will look something like:
   # /home/username/.local/share/virtualenvs/active-annotate-XXXXXXXX

4. Update ``pyrightconfig.json`` with your specific paths:

.. code-block:: json

   {
     "venvPath": "/home/username/.local/share/virtualenvs",
     "venv": "active-annotate-XXXXXXXX"
   }

**Note**: The ``pyrightconfig.json`` file is gitignored because virtual environment paths are specific to each developer's setup.

What Pyright Does
~~~~~~~~~~~~~~~~~

Pyright performs static type analysis to:

- **Import validation** - Ensures all imports can be resolved
- **Type checking** - Validates type annotations and catches type mismatches
- **Code quality** - Identifies potential bugs and coding issues
- **IDE support** - Provides better autocomplete and error detection

Running Pyright Manually (Local)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can run Pyright manually to check for type issues when using local development:

.. code-block:: bash

   # Activate pipenv environment
   pipenv shell

   # Run type checking on the entire project
   pipenv run pyright

   # Check specific files or directories
   pipenv run pyright app/
   pipenv run pyright app/main.py

   # Get verbose output
   pipenv run pyright --verbose

Common Pyright Issues
~~~~~~~~~~~~~~~~~~~~~

**Import Errors**: If you see "Import could not be resolved" errors:

1. Ensure your ``pyrightconfig.json`` is correctly configured
2. Verify your virtual environment is activated
3. Check that required packages are installed in the virtual environment

**Type Errors**: If you see type-related errors:

1. Add proper type annotations to your functions
2. Use ``from typing import`` for complex types
3. Consider using ``# type: ignore`` comments for unavoidable issues

Integration with Pre-commit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyright runs automatically as part of the pre-commit hooks. It will:

1. Check all Python files for type issues
2. Validate that imports can be resolved
3. Block commits if there are type checking errors

This ensures type safety across the entire codebase.
