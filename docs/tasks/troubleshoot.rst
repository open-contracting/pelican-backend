Troubleshoot
============

Re-publish a message
--------------------

When a worker fails, instead of re-processing the entire dataset from the beginning, you can try re-publishing the message that caused the failure, after making an attempted fix.

The `RabbitMQ management interface <https://www.rabbitmq.com/management.html>`__ makes it easy to add a message to a queue. For reference, see the sample messages in the :ref:`rabbitmq` section.

For the :ref:`extract<workers-extract>` workers, it might be easier to run the :ref:`manage-add` command with ``--sample INTEGER``.

.. note::

   Workers are :ref:`designed<worker-design>` to be as idempotent as possible. However, it's possible that a worker isn't idempotent. In that case, you might need to revert the changes made by the previous run (and, ideally, update the worker to be idempotent).
