Contributing
============

Read the rest of the documentation to understand how Pelican backend works, and how to perform common tasks.

Setup
-----

Install development dependencies:

.. code-block:: bash

   pip install pip-tools
   pip-sync requirements_dev.txt

Set up the git pre-commit hook:

.. code-block:: bash

   pre-commit install

:doc:`../tasks/database`.

Development
-----------

The default values in the ``settings.py`` file should be appropriate as-is. You can override them by setting environment variables.

You can now :doc:`start workers<../reference/workers>` and run tests:

.. code-block:: bash

   pytest
