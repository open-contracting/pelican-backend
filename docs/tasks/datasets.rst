Manage datasets
===============

.. _create-dataset:

Create a dataset
----------------

.. code-block:: bash

   python -m commands.create_dataset [OPTIONS] SPIDER_YYYY-MM-DD ID

Create a dataset.

--previous-dataset INTEGER  ID of previous dataset for time-based checks.
--sample INTEGER            Number of compiled releases to extract.

This command also updates the lists of OCID prefixes, identifier schemes, and document formats, used by :doc:`field-level quality checks<checks/field>`.

Delete a dataset
----------------

.. code-block:: bash

   python -m commands.delete_dataset [OPTIONS] ID

Delete a dataset.

--include-filtered  Delete any filtered datasets based on this dataset.

The dataset must be in either the ``CHECKED`` or ``DELETED`` phase and the ``OK`` state.
