.. Active Annotate documentation master file, created by
   sphinx-quickstart on Wed Jul 23 09:40:29 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Active Annotate documentation
=============================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.

.. note::

   This project is under active development.

Installation and Setup
======================

Setting up Python Environment with Pipenv
-------------------------------------------

This project uses `pipenv` for dependency management. Follow these steps to set up the development environment:

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
   pipenv install


3. Activate the virtual environment:

.. code-block:: bash

   # Activate the pipenv shell
   pipenv shell

   # Or run commands in the environment without activating
   pipenv run <command>

Setting up Pre-commit Hooks
----------------------------

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

Running Ruff Manually
~~~~~~~~~~~~~~~~~~~~~~

You can run Ruff manually outside of pre-commit hooks:

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


.. toctree::
   :maxdepth: 2
   :caption: Contents:
