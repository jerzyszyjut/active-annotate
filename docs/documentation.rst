Documentation Guide
===================

This documentation uses Sphinx's ``literalinclude`` directive to import code directly from source files, ensuring the documentation stays in sync with the actual codebase.

Code Inclusion with literalinclude
-----------------------------------

Basic Usage
~~~~~~~~~~~

Include entire files:

.. code-block:: rst

   .. literalinclude:: ../app/main.py
      :language: python

Include specific lines:

.. code-block:: rst

   .. literalinclude:: ../tests/conftest.py
      :language: python
      :lines: 6-12

Include line ranges:

.. code-block:: rst

   .. literalinclude:: ../app/core/config.py
      :language: python
      :lines: 1-10, 15-20

Advanced Options
~~~~~~~~~~~~~~~~

**Emphasize specific lines:**

.. code-block:: rst

   .. literalinclude:: ../app/main.py
      :language: python
      :lines: 1-20
      :emphasize-lines: 5, 10-12

**Add line numbers:**

.. code-block:: rst

   .. literalinclude:: ../tests/test_health.py
      :language: python
      :linenos:

**Include with caption:**

.. code-block:: rst

   .. literalinclude:: ../app/main.py
      :language: python
      :caption: FastAPI application setup
      :name: fastapi-main

**Include specific functions/classes by markers:**

You can also use start-after and end-before to include specific sections:

.. code-block:: rst

   .. literalinclude:: ../app/main.py
      :language: python
      :start-after: # Health check endpoint
      :end-before: # End health check

Benefits of literalinclude
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Always up-to-date** - Documentation automatically reflects code changes
- **No duplication** - Single source of truth for code examples
- **Syntax highlighting** - Proper language-specific formatting
- **Reduced maintenance** - No need to manually update code blocks
- **Testing integration** - Example code is actually tested since it's from real files

Example: Current Project Files
------------------------------

Here are examples of including code from our actual project files:

**Configuration settings:**

.. literalinclude:: ../app/core/config.py
   :language: python
   :lines: 1-4
   :caption: Configuration imports and dependencies

**FastAPI app initialization:**

.. literalinclude:: ../app/main.py
   :language: python
   :lines: 5-12

**Test fixture setup:**

.. literalinclude:: ../tests/conftest.py
   :language: python

**Sample test case:**

.. literalinclude:: ../tests/test_health.py
   :language: python


API Documentation with autodoc
===============================

For Python projects, Sphinx can automatically generate documentation from your code's docstrings using the ``autodoc`` extension.

Setup autodoc
--------------

The ``conf.py`` file has been configured with these extensions:

- ``sphinx.ext.autodoc`` - Automatically document Python modules
- ``sphinx.ext.viewcode`` - Add links to source code
- ``sphinx.ext.napoleon`` - Support for Google and NumPy style docstrings

Using autodoc
--------------

You can automatically document modules, classes, and functions:

**Document an entire module:**

.. code-block:: rst

   .. automodule:: myapp.core.config
      :members:

**Document a specific class:**

.. code-block:: rst

   .. autoclass:: myapp.models.User
      :members:

**Document a specific function:**

.. code-block:: rst

   .. autofunction:: myapp.utils.helper_function

Example: Auto-generated Documentation
-------------------------------------

To use autodoc, you would add directives like this to your documentation:

.. code-block:: rst

   .. autoclass:: myapp.models.User
      :members:

This would automatically generate documentation from the class docstrings and type hints.

**Note:** For autodoc to work properly, all project dependencies must be available in the documentation build environment. You may need to install your project dependencies in the documentation build environment or use mock imports for complex dependencies.

Benefits of autodoc
-------------------

- **Automatic updates** - Documentation reflects current docstrings
- **Cross-references** - Automatic linking between related items
- **Type hints** - Shows function signatures and return types
- **Inheritance** - Shows class inheritance relationships

Combined Approach
-----------------

You can combine ``literalinclude`` for code examples and ``autodoc`` for API documentation:

- Use ``literalinclude`` for: tutorials, examples, configuration files
- Use ``autodoc`` for: API reference, class/function documentation

**Best Practice: Embed Documentation in Code**

The most maintainable approach is to write comprehensive docstrings in your code and use autodoc to extract them automatically:

.. code-block:: python

   class UserSettings(BaseSettings):
       """Application settings and configuration.

       This class manages all configuration settings for the application.
       Settings are loaded from environment variables and have sensible defaults.

       Attributes:
           app_name (str): The name of the application.
           version (str): The current version of the app.
       """
       app_name: str = "My Application"
       version: str = "1.0.0"

Then use autodoc to include it in documentation:

.. code-block:: rst

   .. autoclass:: myapp.config.UserSettings
      :members:

**For API Endpoints: Use OpenAPI Documentation**

Instead of manually documenting API endpoints in Sphinx, leverage FastAPI's built-in OpenAPI documentation:

- **Swagger UI**: ``http://localhost:8000/docs`` - Interactive testing
- **ReDoc**: ``http://localhost:8000/redoc`` - Clean reference documentation
- **OpenAPI Schema**: ``http://localhost:8000/openapi.json`` - Machine-readable schema

This approach ensures:

- **Single source of truth** - Documentation lives with the code
- **Always up-to-date** - Changes to functionality update docs automatically
- **Developer-friendly** - Docstrings help during development
- **IDE integration** - Modern IDEs show the docstrings as help text
- **Interactive testing** - Built-in API testing interface
