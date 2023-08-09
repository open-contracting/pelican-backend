Troubleshoot
============

Worker failure
--------------

In general, if a worker fails, the message is not acknowledged. When the worker restarts, the message is redelivered. Workers are :ref:`designed<worker-design>` to be as idempotent as possible, such that message redelivery is handled gracefully. This is typically achieved by publishing any messages immediately before acknowledging the received message, and by writing to the database either:

-  Immediately before publishing any messages and acknowledging the message.
-  After deleting previously written rows.

There are exceptions:

-  To implement the `Aggregator pattern <https://www.enterpriseintegrationpatterns.com/patterns/messaging/Aggregator.html>`__, the :ref:`check-dataset` worker sets the dataset's state to in-progress. Other workers will then acknowledge messages for the same dataset without further processing. However, this means that, if the worker fails, then the redelivery is ignored. To reset a dataset's state and re-publish the corresponding message, run, for example:

   .. code-block:: bash

      ./manage.py dev restart-dataset-check 123

-  The :ref:`workers-extract` workers publish a message for each batch of extracted data. The received message is acknowledged before publishing messages; this avoids a loop of re-publishing messages in case of a recurring error. However, this means that, if the worker fails, then the missing batches are never extracted. It isn't possible to recover from a partial extraction. After fixing the issue, :ref:`manage-add` a new dataset and :ref:`manage-remove` the old dataset.

Debugging workers
-----------------

The `RabbitMQ management interface <https://www.rabbitmq.com/management.html>`__ makes it easy to add a message to a queue. For reference, see the sample messages in the :ref:`rabbitmq` section. For the :ref:`extract<workers-extract>` workers, it might be easier to run the :ref:`manage-add` command with ``--sample INTEGER``.
