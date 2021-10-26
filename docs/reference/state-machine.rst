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
     - Import is in-progress
     - ``extractor`` workers
   * - ``CONTRACTING_PROCESS``
     - ``OK``
     - Import is complete
     - ``extractor`` workers
   * - ``DATASET``
     - ``IN_PROGRESS``
     - Dataset-level checks are in-progress
     - ``checker/dataset``
   * - ``DATASET``
     - ``OK``
     - Dataset-level checks are complete
     - ``checker/dataset``
   * - ``TIME_VARIANCE``
     - ``IN_PROGRESS``
     - Time-based checks are in-progress
     - ``checker/time_variance``
   * - ``TIME_VARIANCE``
     - ``OK``
     - Time-based checks are complete
     - ``checker/time_variance``
   * - ``CHECKED``
     - ``OK``
     - All work is complete
     - ``core/finisher``
   * - ``DELETED``
     - ``OK``
     - The dataset is deleted, but the row is needed for foreign key references
     - ``maintenance_scripts/delete_dataset``

Item
----

.. list-table::
   :header-rows: 1

   * - State
     - Definition
     - Set by
   * - ``IN_PROGRESS``
     - The item's field-level and compiled release-level checks have not yet been performed
     - ``extractor`` workers
   * - ``OK``
     - The item's field-level and compiled release-level checks have been performed
     - ``contracting_process/processor.py``
