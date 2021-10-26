State machine
=============

The ``progress_monitor_dataset`` and ``progress_monitor_item`` tables track the progress of datasets and items.

.. _state-dataset:

Dataset
-------

.. list-table::
   :header-rows: 1

   * - Phase
     - State
     - Definition
     - Set by
   * - ``CONTRACTING_PROCESS``
     - ``IN_PROGRESS``
     - Extraction is in-progress
     - ``workers.extract.*``
   * - ``CONTRACTING_PROCESS``
     - ``OK``
     - Extraction is complete
     - ``workers.extract.*``
   * - ``DATASET``
     - ``IN_PROGRESS``
     - Dataset-level checks are in-progress
     - ``workers.check.dataset``
   * - ``DATASET``
     - ``OK``
     - Dataset-level checks are complete
     - ``workers.check.dataset``
   * - ``TIME_VARIANCE``
     - ``IN_PROGRESS``
     - Time-based checks are in-progress
     - ``workers.check.time_based``
   * - ``TIME_VARIANCE``
     - ``OK``
     - Time-based checks are complete
     - ``workers.check.time_based``
   * - ``CHECKED``
     - ``OK``
     - All work is complete
     - ``workers.report``
   * - ``DELETED``
     - ``OK``
     - The dataset is deleted, but the row is needed for foreign key references
     - ``commands.delete_dataset``

Item
----

.. list-table::
   :header-rows: 1

   * - State
     - Definition
     - Set by
   * - ``IN_PROGRESS``
     - The item's field-level and compiled release-level checks have not yet been performed
     - ``workers.extract.*``
   * - ``OK``
     - The item's field-level and compiled release-level checks have been performed
     - ``contracting_process/processor.py``
