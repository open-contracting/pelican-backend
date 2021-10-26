Workers
=======

Extract
-------

.. _extractor-ocds-kingfisher:

extractor.ocds_kingfisher
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m extractor.ocds_kingfisher

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

extractor.dataset_filter
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m extractor.dataset_filter

Create filtered datasets.

The worker will ignore a message if the dataset is not in the ``CHECKED`` phase.

.. note::

   This worker is only needed if the Pelican frontend is deployed.

Check
-----

checker.contracting_process
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m checker.contracting_process

Perform the field-level and compiled release-level checks.

#. Receive a message
#. Read matching items from the ``data_item`` table
#. Perform field-level checks on each item
#. Perform resource-level checks on each item
#. Marks each item's state as complete
#. Store all results
#. Publish a message

There can be many workers processing the same dataset at the same time. 

checker.dataset
~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m checker.dataset

Perform the dataset-level checks.

#. Receive a message
#. Determine whether field-level and compiled release-level checks have been performed on all items
#. Read the items from the ``data_item`` table, in batches
#. Submit each item to each dataset-level check
#. Store the results from each check
#. Publish a message

To determine whether field-level and compiled release-level checks have been performed on all items, it waits for the dataset to be in the ``CONTRACTING_PROCESS`` phase and ``OK`` state, with all its items in the ``OK`` state (see :doc:`state-machine`).

checker.time_variance
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m checker.time_variance_checker

Perform the time-based checks.

#. Receive a message
#. Read the items from the ``data_item`` table for this dataset and its ancestor, in batches
#. Submit each item pair to each time-based check
#. Store the results from each check
#. Publish a message

Report
------

core.finisher
~~~~~~~~~~~~~

.. code-block:: bash

   python -m core.finisher

Create reports, pick examples, and update dataset metadata.

#. Receive a message
#. Calculate compiled release-level report
#. Prepare (random) examples from compiled release-level checks
#. Calculate field-level report
#. Prepare (random) examples from field-level checks 
#. Update the dataset's metadata
