Contributing
============

Read the rest of the documentation to understand how Pelican backend works, and how to perform common tasks.

Setup
-----

Create a Python 3.8 virtual environment.

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

You can now:

-  :doc:`Start workers<../reference/workers>`

   .. tip::

      Set the ``LOG_LEVEL`` environment variable to ``DEBUG`` to see log messages about message processing. For example:

      .. code-block:: bash

         env LOG_LEVEL=DEBUG python -m workers.extract.kingfisher_process

   .. note::

      Remember: `Consumers declare and bind queues, not publishers <https://ocp-software-handbook.readthedocs.io/en/latest/services/rabbitmq.html#bindings>`__. Start each worker before publishing messages.

-  Run tests:

   .. code-block:: bash

      pytest

Having trouble? See :doc:`../tasks/troubleshoot`.

Defensive programming
~~~~~~~~~~~~~~~~~~~~~

There are innumerable ways in which OCDS data can have structural errors. Although such data should not be submitted for processing, we nonetheless try to guard against it. Use the functions from the :mod:`pelican.util.getter` module to access data safely.

.. _testing:

Testing
-------

Define any OCDS data as as a dict or a list-of-dicts in the global scope. This allows the ``test_fixtures.py`` file to check its conformance to OCDS (after adding any required fields).

If the OCDS data is required to be invalid, you can suffix ``__invalid_schema`` to the variable's name. However, try to make the OCDS data valid, if possible. For example:

-  If you need a currency whose rate is unknown, use ``"UYW"``.
-  If you need duplicate IDs, but the tests are failing with "… has non-unique elements", add a valid field like ``"name": ""`` or ``"title": ""`` to make the items distinct.

This ensures that checks work against valid OCDS data – not artificial date created for testing.

Maintenance
~~~~~~~~~~~

.. _code-fixtures:

Code fixtures
^^^^^^^^^^^^^

For :ref:`test_fixtures.py<testing>` to work, check that all OCDS data is in the global scope. For each type of check, there should be …

Compiled release-level checks
  In ``tests/compiled_release/*``, no results for ``calculate\((?!\w+\)|{}\))``, and the results for ``import (?!bootstrap|calculate|functools|get_empty_result_resource)`` should be followed by a statement like ``calculate = functools.partial(roles.calculate_path_role, ...)``
Dataset-level checks
  No results for ``add_item\((?!\w+, \w+(\[\w+\])?, \w+( \+ \d+)?\))``
Time-based checks
  No results for ``\b(filter|evaluate)\((?!\w+, \w+, \w+, \w+, \w+\))``

Any exceptions to the above must be moved to the global scope, or manually validated.

OCDS upgrades
^^^^^^^^^^^^^

-  Update file fixtures:

   .. code-block:: bash

      curl -sS https://raw.githubusercontent.com/open-contracting/sample-data/main/blank-template/release-template-1__1__5.json -o tests/fixtures/blank.json
      curl -sS https://raw.githubusercontent.com/open-contracting/sample-data/main/fictional-example/1.1/record/ocds-213czf-000-00001.json | jq '.records[0].compiledRelease' > tests/fixtures/compiled-release.json

-  Review ``definitions.py`` files, to be sure that checks account for new fields.
-  Update :ref:`code fixtures<code-fixtures>` to use new fields.
-  Decide whether to add new checks for new fields.
