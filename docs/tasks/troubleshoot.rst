Troubleshoot
============

Worker failure
--------------

.. seealso::

   :ref:`worker-design`

Workers make state changes as late as possible, and acknowledge messages once processing is complete. There are exceptions:

-  To implement the `Aggregator pattern <https://www.enterpriseintegrationpatterns.com/patterns/messaging/Aggregator.html>`__, the :ref:`check-dataset` worker sets the dataset's state to in-progress before doing work. The worker will then acknowledge messages for the same dataset without further processing. However, this means that, if the worker fails, then the redelivery is ignored. To reset a dataset's state and re-publish the corresponding message, run, for example:

   .. code-block:: bash

      ./manage.py dev restart-dataset-check 123

-  In the :ref:`workers-extract` workers, the message is acknowledged before publishing a message for each batch of extracted data. This avoids `cascading redelivery <https://ocp-software-handbook.readthedocs.io/en/latest/services/rabbitmq.html#idempotence>`__, as there is logic that can fail between each publish. However, this means that, if the worker fails, then the missing batches are never extracted. After fixing the issue, :ref:`manage-add` a new dataset and :ref:`manage-remove` the old dataset.

Debugging workers
-----------------

The `RabbitMQ management interface <https://www.rabbitmq.com/management.html>`__ makes it easy to add a message to a queue. For reference, see the sample messages in the :ref:`rabbitmq` section. For the :ref:`extract<workers-extract>` workers, it might be easier to run the :ref:`manage-add` command with ``--sample INTEGER``.
