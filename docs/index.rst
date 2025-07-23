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

- Check code formatting
- Lint code for potential issues
- Ensure consistent code style
- Run other quality checks as configured

If any hooks fail, the commit will be blocked until you fix the issues.

Updating Dependencies
---------------------

To update project dependencies:

.. code-block:: bash

   # Update all dependencies to latest compatible versions
   pipenv update

   # Update a specific package
   pipenv update <package-name>

   # Add a new dependency
   pipenv install <package-name>


.. toctree::
   :maxdepth: 2
   :caption: Contents:
