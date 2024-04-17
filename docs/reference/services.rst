Services
========

.. _rabbitmq:

RabbitMQ
--------

.. seealso::

   -  :ref:`worker-design`
   -  Having trouble? See :doc:`../tasks/troubleshoot`

This project uses a direct exchange in the same way as the `default exchange <https://www.rabbitmq.com/tutorials/amqp-concepts.html#exchange-default>`__, in which every queue is bound using a routing key that is the same as the queue's name.

In each worker, the queue name and binding key is set by ``consume_routing_key``, and the routing key of published messages is set by ``routing_key``. Queue names and routing keys are prefixed by the exchange name, set by the ``RABBIT_EXCHANGE_NAME`` environment variable.

.. list-table::
   :header-rows: 1

   * - Worker/Command
     - Queue (input)
     - Message routing key (output)
     - Sample message
   * - ``manage.py add``
     - N/A
     - ``ocds_kingfisher_extractor_init``
     - :ref:`manage-add` command
   * - ``workers.extract.kingfisher_process``
     - ``ocds_kingfisher_extractor_init``
     - ``extractor``
     - ``{"dataset_id": 1, "item_ids": [1,2,3]}``
   * - ``workers.extract.dataset_filter``
     - ``dataset_filter_extractor_init``
     - ``extractor``
     - ``{"dataset_id": 1, "item_ids": [1,2,3]}``
   * - ``workers.check.data_item``
     - ``extractor``
     - ``contracting_process_checker``
     - ``{"dataset_id": 123}``
   * - ``workers.check.dataset``
     - ``contracting_process_checker``
     - ``dataset_checker``
     - ``{"dataset_id": 123}``
   * - ``workers.check.time_based``
     - ``dataset_checker``
     - ``time_variance_checker``
     - ``{"dataset_id": 123}``
   * - ``workers.report``
     - ``time_variance_checker``
     - N/A
     - N/A
   * - ``workers.wipe``
     - ``wiper_init``
     - N/A
     - N/A

.. _postgresql:

PostgreSQL
----------

Tables
~~~~~~

.. list-table::
   :header-rows: 1

   * - Table
     - Description
     - ``INSERT`` by
     - ``SELECT`` by
   * - ``dataset``
     - Extracted collections
     - ``workers.extract``
     - ``workers.extract.dataset_filter``, ``dataset/meta_data_aggregator``, ``time_variance/processor``
   * - ``data_item``
     - Extracted compiled releases
     - ``workers.extract``
     - ``workers.check.data_item``, ``dataset/processor``, ``time_variance/processor``
   * - ``field_level_check``
     - Field-level check results
     - ``contracting_process/processor``
     - ``contracting_process/field_level/report_examples``
   * - ``field_level_check_examples``
     - Field-level check examples
     - ``contracting_process/processor``
     - ``contracting_process/field_level/report_examples``
   * - ``resource_level_check``
     - Compiled release-level check results
     - ``contracting_process/processor``
     - ``contracting_process/resource_level/examples``, ``contracting_process/resource_level/report``
   * - ``resource_level_check_examples``
     - Compiled release-level check examples
     - ``contracting_process/processor``
     - ``contracting_process/resource_level/examples``
   * - ``dataset_level_check``
     - Dataset-level check results
     - ``dataset/processor``
     - N/A
   * - ``time_variance_level_check``
     - Time-based check results
     - ``time_variance/processor``
     - N/A
   * - ``progress_monitor_dataset``
     - Progress of datasets' processing (see :doc:`state-machine`)
     - ``workers.extract``, ``workers.check``, ``workers.report``
     - ``workers.extract.dataset_filter``, ``workers.check.dataset``
   * - ``progress_monitor_item``
     - Progress of items' processing (see :doc:`state-machine`)
     - ``workers.extract``, ``contracting_process/processor``
     - ``workers.check.dataset``

.. image:: ../_static/erd.png
   :target: ../_static/erd.png

.. See https://ocp-software-handbook.readthedocs.io/en/latest/services/postgresql.html#entity-relationship-diagram and use relationships.real.large.png

.. image:: ../_static/exchange_rates.png
   :target: ../_static/exchange_rates.png
