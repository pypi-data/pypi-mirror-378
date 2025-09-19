============
Contributing
============

We welcome contributions to the city2graph project! This document provides guidelines for contributing to the project.

Setting Up Development Environment
---------------------------------

1. Fork the repository on GitHub.
2. Clone your fork locally:

   .. code-block:: bash

       git clone https://github.com/<your-name>/city2graph.git
       cd city2graph
       git remote add upstream https://github.com/c2g-dev/city2graph.git

3. Set up the development environment:

   .. code-block:: bash

       uv sync --group dev --extra cpu
       source .venv/bin/activate  # On Windows: .venv\Scripts\activate

Making Changes
-------------

1. Create a new branch for your changes:

   .. code-block:: bash

       git checkout -b feature/your-feature-name

2. Make your changes to the codebase.

3. Run pre-commit checks before committing:

   .. code-block:: bash

       uv run pre-commit run --all-files

4. Run the tests to ensure your changes don't break existing functionality:

   .. code-block:: bash

       uv run pytest --cov=city2graph --cov-report=html --cov-report=term

5. Update or add documentation as needed.
6. Commit your changes with a descriptive commit message.

Code Style
---------

We follow strict code quality standards using the following tools:

* **Ruff**: For linting and formatting Python code
* **mypy**: For static type checking
* **numpydoc**: For docstring style validation

Key style guidelines:

* Use 4 spaces for indentation.
* Maximum line length of 88 characters.
* Use docstrings following numpydoc conventions for all public modules, functions, classes, and methods.
* Use type hints where appropriate.

Pre-commit hooks will automatically run these checks when you commit changes.

Documentation
------------

When contributing new features or making significant changes, please update the documentation:

1. Add docstrings to all public functions, classes, and methods.
2. Update the relevant documentation files in the ``docs/source`` directory.
3. If adding a new feature, consider adding an example to ``docs/source/examples.rst``.

Pull Requests
------------

1. Push your changes to your fork:

   .. code-block:: bash

       git push origin feature/your-feature-name

2. Open a pull request on GitHub.
3. Describe your changes in the pull request description.
4. Reference any related issues that your pull request addresses.

Your pull request will be reviewed, and you may be asked to make changes before it's merged.

Building Documentation
--------------------

To build and preview the documentation locally:

1. Create and activate a virtual environment with uv:

   .. code-block:: bash

       uv venv docs-env
       source docs-env/bin/activate  # On Windows: docs-env\Scripts\activate

2. Install documentation dependencies:

   .. code-block:: bash

       uv pip install -e ".[docs]"

3. Build the documentation:

   .. code-block:: bash

       cd docs
       make html

4. Open ``docs/build/html/index.html`` in your browser to view the documentation.
