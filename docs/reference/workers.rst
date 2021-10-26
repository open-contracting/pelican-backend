Workers
=======

.. _workers-extract:

Extract
-------

.. _extract-kingfisher-process:

extract.kingfisher_process
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m workers.extract.kingfisher_process

Extract collections from Kingfisher Process.

#. Receive a message
#. Select data IDs for the matching collection in Kingfisher Process
#. Create the dataset
#. Update the dataset's metadata
#. Acknowledge the message (`point-of-no-return <https://ocp-software-handbook.readthedocs.io/en/latest/services/rabbitmq.html#acknowledgements>`__)
#. Select compiled releases from Kingfisher Process, in batches
#. Insert compiled releases into the ``data_item`` table
#. Initializes each item's state as in-progress
#. Publishes a message with batches of item IDs

extract.dataset_filter
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m workers.extract.dataset_filter

Create filtered datasets.

The worker will ignore a message if the dataset is not in the ``CHECKED`` phase.

.. note::

   This worker is only needed if the Pelican frontend is deployed.

Check
-----

.. _check-data-item:

check.data_item
~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m workers.check.data_item

Perform the field-level and compiled release-level checks.

#. Receive a message
#. Read matching items from the ``data_item`` table
#. Perform field-level checks on each item
#. Perform resource-level checks on each item
#. Marks each item's state as complete
#. Store all results
#. Publish a message

There can be many workers processing the same dataset at the same time. 

.. _check-dataset:

check.dataset
~~~~~~~~~~~~~

.. code-block:: bash

   python -m workers.check.dataset

Perform the dataset-level checks.

#. Receive a message
#. Determine whether field-level and compiled release-level checks have been performed on all items
#. Read the items from the ``data_item`` table, in batches
#. Submit each item to each dataset-level check
#. Store the results from each check
#. Publish a message

To determine whether field-level and compiled release-level checks have been performed on all items, it waits for the dataset to be in the ``CONTRACTING_PROCESS`` phase and ``OK`` state, with all its items in the ``OK`` state (see :doc:`state-machine`).

.. _check-time-based:

check.time_based
~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m workers.check.time_based

Perform the time-based checks.

#. Receive a message
#. Read the items from the ``data_item`` table for this dataset and its ancestor, in batches
#. Submit each item pair to each time-based check
#. Store the results from each check
#. Publish a message

Others
------

.. _report:

report
~~~~~~

.. code-block:: bash

   python -m workers.report

Create reports, pick examples, and update dataset metadata.

#. Receive a message
#. Calculate compiled release-level report
#. Prepare (random) examples from compiled release-level checks
#. Calculate field-level report
#. Prepare (random) examples from field-level checks 
#. Update the dataset's metadata
