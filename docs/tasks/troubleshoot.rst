Troubleshoot
============

Re-publish a message
--------------------

When a worker fails, instead of re-processing the entire dataset from the beginning, you can try re-publishing the message that caused the failure, after making an attempted fix.

The `RabbitMQ management interface <https://www.rabbitmq.com/management.html>`__ makes it easy to add a message to a queue. For reference, see the sample messages in the :ref:`rabbitmq` section.

For the ``extractor`` workers, it might be easier to :ref:`add-dataset` with ``--sample INTEGER``.

.. note::

   Workers are :ref:`designed<worker-design>` to be as idempotent as possible. However, it's possible that a worker isn't idempotent. In that case, you might need to revert the changes made by the previous run (and, ideally, update the worker to be idempotent).

Submit a command
----------------

Some workers accept special messages that contain a ``"command"`` key. Presently, its value has no effect, so it can be set to ``true``. These messages are only created by administrators, not by code.


.. list-table::
   :header-rows: 1

   * - Worker
     - Sample message
     - Effect
   * - ``extractor.ocds_kingfisher``
     - ``{"command": true, "dataset_id": 123}``
     - -  Sets the :ref:`dataset's state<state-dataset>` to ``CONTRACTING_PROCESS`` and ``IN_PROGRESS``
       -  Sets the dataset's size to the number of related items in the ``data_item`` table
       -  Performs the same steps :ref:`as usual<extractor-ocds-kingfisher>` that follow the point-of-no-return

       In short, if the extractor had failed, this causes the field-level and compiled release-level checks to start.
   * - ``checker.contracting_process``
     - ``{"command": true, "dataset_id": 123}``
     - -  Sets the :ref:`dataset's state<state-dataset>` to ``CONTRACTING_PROCESS`` and ``OK``
       -  Publishes a :ref:`message<rabbitmq>`

       In short, assuming field-level and compiled release-level checks have been performed on all items, this causes the dataset-level checks to start.
