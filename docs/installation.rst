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
