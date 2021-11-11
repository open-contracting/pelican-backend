Manage datasets
===============

A CLI interface is provided via the ``./manage.py`` script, with the following commands.

.. _manage-add:

add
---

.. code-block:: bash

   ./manage.py add [OPTIONS] SPIDER_YYYY-MM-DD ID

Create a dataset.

--previous-dataset INTEGER  ID of previous dataset for time-based checks.
--sample INTEGER            Number of compiled releases to extract.

.. _manage-remove:

remove
------

.. code-block:: bash

   ./manage.py remove [OPTIONS] ID

Delete a dataset.

--include-filtered  Delete any filtered datasets based on this dataset.

The dataset must be in either the ``CHECKED`` or ``DELETED`` phase and the ``OK`` state.
