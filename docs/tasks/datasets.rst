Add datasets
============

.. _add-dataset:

Add a dataset
-------------

.. code-block:: bash

   python -m core.starter [OPTIONS] SPIDER_YYYY-MM-DD ID

--previous-dataset INTEGER  ID of previous dataset for time-based checks.
--sample INTEGER            Number of compiled releases to import.

This command also updates the lists of OCID prefixes, identifier schemes, and document formats, used by :doc:`field-level quality checks<checks/field>`.

Remove a dataset
----------------

.. code-block:: bash

   python -m maintenance_scripts.delete_dataset [OPTIONS] ID

--include-filtered  Delete any filtered datasets based on this dataset.

The dataset must be in either the ``CHECKED`` or ``DELETED`` phase and the ``OK`` state.
